from __future__ import annotations

import importlib.util
import inspect
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np


class OptimizationError(Exception):
    """Base exception for errors in the optimization module."""


class FitnessFileError(OptimizationError):
    """Raised when the fitness file is missing, invalid, or cannot be imported."""


class FitnessExecutionError(OptimizationError):
    """Raised when the fitness function fails during execution or returns an invalid value."""


class InvalidParameterError(OptimizationError):
    """Raised when algorithm parameters or search space bounds are invalid."""


@dataclass
class ParameterSpec:
    name: str
    label: str
    param_type: str  # 'int', 'float', 'choice', 'bool', 'seed'
    default: Any
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    step: Optional[float] = None
    decimals: int = 3
    choices: Optional[List[str]] = None
    tooltip: str = ""


@dataclass
class OptimizationResult:
    algorithm_key: str
    algorithm_name: str
    status: str  # "Completed" | "Cancelled"
    best_fitness: float
    best_position: np.ndarray
    iterations_executed: int
    total_iterations: int
    history_best: List[float] = field(default_factory=list)
    history_mean: List[float] = field(default_factory=list)
    history_diversity: List[float] = field(default_factory=list)
    objective: str = "Minimize"
    fitness_file: str = ""
    fitness_func_name: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)


class FitnessLoader:
    """
    Centralized contract for loading, validating, and invoking a Python (.py) fitness function.
    """
    CANDIDATE_NAMES: Tuple[str, ...] = (
        "fitness",
        "fitness_function",
        "objective",
        "objective_function",
        "evaluate",
        "cost",
        "loss",
    )

    @classmethod
    def validate_file_path(cls, file_path: str) -> str:
        if not file_path or not str(file_path).strip():
            raise FitnessFileError("No fitness function file selected. Please import a .py file.")

        norm_path = os.path.abspath(str(file_path).strip())
        if not os.path.exists(norm_path) or not os.path.isfile(norm_path):
            raise FitnessFileError(f"Fitness file not found:\n{norm_path}")

        if not norm_path.lower().endswith(".py"):
            raise FitnessFileError("Invalid file extension. The fitness function file must be a Python file (.py).")

        return norm_path

    @classmethod
    def _import_module(cls, file_path: str):
        norm_path = cls.validate_file_path(file_path)
        module_name = f"_quantyx_fitness_{os.path.splitext(os.path.basename(norm_path))[0]}"

        try:
            spec = importlib.util.spec_from_file_location(module_name, norm_path)
            if spec is None or spec.loader is None:
                raise FitnessFileError(f"Could not create module specification for:\n{norm_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module, norm_path
        except FitnessFileError:
            raise
        except SyntaxError as e:
            raise FitnessFileError(
                f"Syntax error while importing fitness file '{os.path.basename(norm_path)}' "
                f"(line {e.lineno}):\n{e.msg}"
            ) from e
        except Exception as e:
            raise FitnessFileError(
                f"Error importing fitness file '{os.path.basename(norm_path)}':\n{str(e)}"
            ) from e

    @classmethod
    def inspect_functions(cls, file_path: str) -> Tuple[List[str], str, Dict[str, Any]]:
        """
        Imports the .py file and returns (all_function_names, default_function_name, metadata).
        """
        module, norm_path = cls._import_module(file_path)

        user_functions = [
            (name, obj)
            for name, obj in inspect.getmembers(module, inspect.isfunction)
            if not name.startswith("_") and getattr(obj, "__module__", None) == module.__name__
        ]
        user_functions.sort(key=lambda item: getattr(getattr(item[1], "__code__", None), "co_firstlineno", 0))

        func_names = [name for name, _ in user_functions]
        if not func_names:
            raise FitnessFileError(
                f"No callable function found in '{os.path.basename(norm_path)}'.\n"
                f"Define at least one function (e.g. 'def fitness(x):') in the Python file."
            )

        default_name = func_names[0]
        for candidate in cls.CANDIDATE_NAMES:
            if candidate in func_names:
                default_name = candidate
                break

        metadata: Dict[str, Any] = {}
        for attr in ("BOUNDS", "N_VARS", "OBJECTIVE"):
            if hasattr(module, attr):
                metadata[attr] = getattr(module, attr)

        return func_names, default_name, metadata

    @classmethod
    def load(
        cls,
        file_path: str,
        function_name: Optional[str] = None,
    ) -> Tuple[Callable[[np.ndarray], float], str, Dict[str, Any]]:
        """
        Loads a .py file and returns (wrapped_fitness_callable, function_name, metadata).
        If function_name is specified, loads that exact function from the file.
        """
        module, norm_path = cls._import_module(file_path)
        func_names, default_name, metadata = cls.inspect_functions(file_path)

        chosen_name = (function_name or "").strip() or default_name
        target_fn = getattr(module, chosen_name, None)
        if not callable(target_fn):
            raise FitnessFileError(
                f"Function '{chosen_name}' was not found or is not callable in '{os.path.basename(norm_path)}'.\n"
                f"Available functions: {', '.join(func_names)}"
            )

        wrapped_fn = cls._wrap_callable(target_fn, chosen_name)
        return wrapped_fn, chosen_name, metadata

    @classmethod
    def _wrap_callable(cls, fn: Callable, fn_name: str) -> Callable[[np.ndarray], float]:
        # Inspect signature to support both fitness(x) and fitness(x1, x2, ...)
        unpack_args = False
        try:
            sig = inspect.signature(fn)
            params = [
                p for p in sig.parameters.values()
                if p.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            has_varargs = any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in sig.parameters.values())
            if len(params) > 1 and not has_varargs:
                unpack_args = True
        except (ValueError, TypeError):
            unpack_args = False

        def evaluate(x: np.ndarray) -> float:
            arr = np.asarray(x, dtype=float)
            try:
                if unpack_args:
                    raw_val = fn(*arr.tolist())
                else:
                    try:
                        raw_val = fn(arr)
                    except TypeError:
                        raw_val = fn(*arr.tolist())
            except Exception as e:
                raise FitnessExecutionError(
                    f"Error executing fitness function '{fn_name}':\n{str(e)}"
                ) from e

            if raw_val is None or isinstance(raw_val, bool):
                raise FitnessExecutionError(
                    f"Fitness function '{fn_name}' must return a numeric scalar value, got {type(raw_val).__name__}."
                )

            try:
                scalar_arr = np.asarray(raw_val, dtype=float)
                if scalar_arr.size != 1:
                    raise FitnessExecutionError(
                        f"Fitness function '{fn_name}' must return a single scalar value, "
                        f"got shape {scalar_arr.shape}."
                    )
                val = float(scalar_arr.item())
            except FitnessExecutionError:
                raise
            except Exception as e:
                raise FitnessExecutionError(
                    f"Fitness function '{fn_name}' returned a non-numeric result: {raw_val!r}"
                ) from e

            if not np.isfinite(val):
                raise FitnessExecutionError(
                    f"Fitness function '{fn_name}' returned a non-finite value ({val})."
                )
            return val

        return evaluate


def parse_and_validate_bounds(
    n_vars: Any,
    lower_bound_input: Any,
    upper_bound_input: Any,
) -> List[Tuple[float, float]]:
    """
    Validates the number of variables and parses lower/upper bounds.
    Accepts either a single scalar value (applied to all dimensions) or
    comma-separated values matching n_vars.
    """
    try:
        n_dim = int(n_vars)
    except (ValueError, TypeError) as e:
        raise InvalidParameterError("Number of variables must be a valid integer.") from e

    if n_dim < 1 or n_dim > 1000:
        raise InvalidParameterError("Number of variables must be between 1 and 1000.")

    def _parse_bound(raw: Any, label: str) -> List[float]:
        if isinstance(raw, (int, float, np.number)) and not isinstance(raw, bool):
            val = float(raw)
            if not np.isfinite(val):
                raise InvalidParameterError(f"{label} must be a finite number.")
            return [val] * n_dim

        text = str(raw).strip()
        if not text:
            raise InvalidParameterError(f"{label} cannot be empty.")

        parts = [p.strip() for p in text.replace(";", ",").split(",") if p.strip() != ""]
        if not parts:
            raise InvalidParameterError(f"{label} contains no valid numeric values.")

        values: List[float] = []
        for p in parts:
            try:
                v = float(p)
            except ValueError as e:
                raise InvalidParameterError(f"Invalid numeric value '{p}' in {label}.") from e
            if not np.isfinite(v):
                raise InvalidParameterError(f"{label} must contain finite numeric values.")
            values.append(v)

        if len(values) == 1:
            return values * n_dim
        if len(values) != n_dim:
            raise InvalidParameterError(
                f"{label} has {len(values)} values, but Number of Variables is {n_dim}.\n"
                f"Provide either a single value or {n_dim} comma-separated values."
            )
        return values

    lowers = _parse_bound(lower_bound_input, "Lower Bound")
    uppers = _parse_bound(upper_bound_input, "Upper Bound")

    bounds: List[Tuple[float, float]] = []
    for idx, (lb, ub) in enumerate(zip(lowers, uppers)):
        if lb >= ub:
            raise InvalidParameterError(
                f"Inconsistent bounds at variable x[{idx}]: Lower Bound ({lb}) must be strictly "
                f"less than Upper Bound ({ub})."
            )
        bounds.append((lb, ub))

    return bounds


def parse_random_seed(raw_seed: Any) -> Optional[int]:
    if raw_seed is None:
        return None
    if isinstance(raw_seed, bool):
        raise InvalidParameterError("Random Seed must be an integer or empty.")
    if isinstance(raw_seed, (int, np.integer)):
        if int(raw_seed) < 0:
            raise InvalidParameterError("Random Seed must be a non-negative integer.")
        return int(raw_seed)

    text = str(raw_seed).strip()
    if text == "" or text.lower() == "none":
        return None
    try:
        seed_val = int(text)
    except ValueError as e:
        raise InvalidParameterError(f"Invalid Random Seed '{text}'. Please enter a valid integer or leave blank.") from e
    if seed_val < 0:
        raise InvalidParameterError("Random Seed must be a non-negative integer.")
    return seed_val


def compute_population_diversity(
    positions: np.ndarray,
    lb: np.ndarray,
    ub: np.ndarray,
) -> float:
    """
    Computes population/swarm diversity as the mean root-mean-square (RMS) normalized
    distance of individuals to the population centroid across all decision variables.
    Returns 0.0 when the population converges to a single point.
    """
    if positions is None or len(positions) <= 1:
        return 0.0
    span = np.where((ub - lb) > 1e-12, (ub - lb), 1.0)
    norm_pos = (positions - lb) / span
    centroid = np.mean(norm_pos, axis=0)
    rms_dist_per_ind = np.sqrt(np.mean((norm_pos - centroid) ** 2, axis=1))
    return float(np.mean(rms_dist_per_ind))


class BaseOptimizer(ABC):
    """
    Common abstract interface for optimization algorithms.
    Designed so new algorithms (e.g., DE, SA, CMA-ES) can be registered seamlessly.
    """
    key: str = ""
    display_name: str = ""

    @classmethod
    @abstractmethod
    def get_parameter_specs(cls) -> List[ParameterSpec]:
        raise NotImplementedError

    @classmethod
    def validate_parameters(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        validated: Dict[str, Any] = {}
        for spec in cls.get_parameter_specs():
            raw = params.get(spec.name, spec.default)
            if spec.param_type == "int":
                try:
                    if isinstance(raw, bool):
                        raise ValueError("Boolean is not a valid int parameter.")
                    val = int(raw)
                except (ValueError, TypeError) as e:
                    raise InvalidParameterError(f"Parameter '{spec.label.rstrip(':')}' must be an integer.") from e
                if spec.min_val is not None and val < spec.min_val:
                    raise InvalidParameterError(
                        f"Parameter '{spec.label.rstrip(':')}' must be >= {int(spec.min_val)}."
                    )
                if spec.max_val is not None and val > spec.max_val:
                    raise InvalidParameterError(
                        f"Parameter '{spec.label.rstrip(':')}' must be <= {int(spec.max_val)}."
                    )
                validated[spec.name] = val

            elif spec.param_type == "float":
                try:
                    if isinstance(raw, bool):
                        raise ValueError("Boolean is not a valid float parameter.")
                    val = float(raw)
                except (ValueError, TypeError) as e:
                    raise InvalidParameterError(f"Parameter '{spec.label.rstrip(':')}' must be a number.") from e
                if not np.isfinite(val):
                    raise InvalidParameterError(f"Parameter '{spec.label.rstrip(':')}' must be finite.")
                if spec.min_val is not None and val < spec.min_val:
                    raise InvalidParameterError(
                        f"Parameter '{spec.label.rstrip(':')}' must be >= {spec.min_val}."
                    )
                if spec.max_val is not None and val > spec.max_val:
                    raise InvalidParameterError(
                        f"Parameter '{spec.label.rstrip(':')}' must be <= {spec.max_val}."
                    )
                validated[spec.name] = val

            elif spec.param_type == "choice":
                val = str(raw)
                if spec.choices and val not in spec.choices:
                    raise InvalidParameterError(
                        f"Invalid option '{val}' for '{spec.label.rstrip(':')}'. "
                        f"Allowed: {', '.join(spec.choices)}."
                    )
                validated[spec.name] = val

            elif spec.param_type == "bool":
                validated[spec.name] = bool(raw)

            elif spec.param_type == "seed":
                validated[spec.name] = parse_random_seed(raw)

            else:
                validated[spec.name] = raw

        return validated

    @abstractmethod
    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        bounds: List[Tuple[float, float]],
        params: Dict[str, Any],
        objective: str = "Minimize",
        progress_callback: Optional[Callable[[int, int, float, np.ndarray, List[float]], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> OptimizationResult:
        raise NotImplementedError


class GeneticAlgorithmOptimizer(BaseOptimizer):
    key = "GA"
    display_name = "GA - Genetic Algorithm"

    @classmethod
    def get_parameter_specs(cls) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="population_size",
                label="Population Size:",
                param_type="int",
                default=50,
                min_val=4,
                max_val=10000,
                tooltip="Number of candidate individuals in each generation (default: 50).",
            ),
            ParameterSpec(
                name="num_generations",
                label="Number of Generations:",
                param_type="int",
                default=100,
                min_val=1,
                max_val=100000,
                tooltip="Total number of evolutionary generations to execute (default: 100).",
            ),
            ParameterSpec(
                name="crossover_rate",
                label="Crossover Rate:",
                param_type="float",
                default=0.8,
                min_val=0.0,
                max_val=1.0,
                step=0.05,
                decimals=3,
                tooltip="Probability of recombination between parent individuals (0.0 to 1.0, default: 0.8).",
            ),
            ParameterSpec(
                name="mutation_rate",
                label="Mutation Rate:",
                param_type="float",
                default=0.1,
                min_val=0.0,
                max_val=1.0,
                step=0.02,
                decimals=3,
                tooltip="Probability of gene mutation per variable (0.0 to 1.0, default: 0.1).",
            ),
            ParameterSpec(
                name="selection_method",
                label="Selection Method:",
                param_type="choice",
                default="Tournament",
                choices=["Tournament", "Roulette Wheel", "Rank"],
                tooltip="Parent selection strategy: Tournament, Roulette Wheel, or Rank selection.",
            ),
            ParameterSpec(
                name="elitism",
                label="Elitism:",
                param_type="bool",
                default=True,
                tooltip="Preserves the best individual(s) unchanged into the next generation.",
            ),
            ParameterSpec(
                name="random_seed",
                label="Random Seed:",
                param_type="seed",
                default="42",
                tooltip="Integer seed for reproducibility (leave blank for random behavior).",
            ),
        ]

    def _select_parents(
        self,
        rng: np.random.Generator,
        population: np.ndarray,
        internal_costs: np.ndarray,
        method: str,
        n_parents: int,
    ) -> np.ndarray:
        pop_size = len(population)
        if method == "Tournament":
            k = min(3, pop_size)
            competitors = rng.integers(0, pop_size, size=(n_parents, k))
            comp_costs = internal_costs[competitors]
            winners = competitors[np.arange(n_parents), np.argmin(comp_costs, axis=1)]
            return population[winners].copy()

        elif method == "Roulette Wheel":
            # Convert minimization cost into positive selection weights
            max_c = np.max(internal_costs)
            weights = (max_c - internal_costs) + 1e-9
            prob_sum = np.sum(weights)
            if prob_sum <= 0 or not np.isfinite(prob_sum):
                probs = np.full(pop_size, 1.0 / pop_size)
            else:
                probs = weights / prob_sum
            indices = rng.choice(pop_size, size=n_parents, replace=True, p=probs)
            return population[indices].copy()

        else:  # Rank
            order = np.argsort(internal_costs)  # best (lowest cost) first
            ranks = np.empty(pop_size, dtype=float)
            ranks[order] = np.arange(pop_size, 0, -1, dtype=float)
            probs = ranks / np.sum(ranks)
            indices = rng.choice(pop_size, size=n_parents, replace=True, p=probs)
            return population[indices].copy()

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        bounds: List[Tuple[float, float]],
        params: Dict[str, Any],
        objective: str = "Minimize",
        progress_callback: Optional[Callable[[int, int, float, np.ndarray, List[float]], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> OptimizationResult:
        clean_params = self.validate_parameters(params)
        pop_size: int = clean_params["population_size"]
        n_generations: int = clean_params["num_generations"]
        crossover_rate: float = clean_params["crossover_rate"]
        mutation_rate: float = clean_params["mutation_rate"]
        selection_method: str = clean_params["selection_method"]
        use_elitism: bool = clean_params["elitism"]
        seed: Optional[int] = clean_params["random_seed"]

        is_maximize = str(objective).strip().lower().startswith("max")
        sign = -1.0 if is_maximize else 1.0

        rng = np.random.default_rng(seed)
        n_dim = len(bounds)
        lb = np.array([b[0] for b in bounds], dtype=float)
        ub = np.array([b[1] for b in bounds], dtype=float)
        span = ub - lb

        population = rng.uniform(lb, ub, size=(pop_size, n_dim))
        raw_fitness = np.array([fitness_fn(ind) for ind in population], dtype=float)
        internal_costs = sign * raw_fitness

        best_idx = int(np.argmin(internal_costs))
        best_fitness = float(raw_fitness[best_idx])
        best_position = population[best_idx].copy()

        history_best: List[float] = []
        history_mean: List[float] = []
        history_diversity: List[float] = []
        generations_done = 0
        status = "Completed"

        n_elite = max(1, min(2, pop_size - 1)) if use_elitism else 0

        for gen in range(1, n_generations + 1):
            if cancel_check is not None and cancel_check():
                status = "Cancelled"
                break

            elite_Order = np.argsort(internal_costs)
            elites = population[elite_Order[:n_elite]].copy() if n_elite > 0 else np.empty((0, n_dim))

            parents = self._select_parents(rng, population, internal_costs, selection_method, pop_size)
            offspring = np.empty_like(population)

            for i in range(0, pop_size, 2):
                p1 = parents[i]
                p2 = parents[min(i + 1, pop_size - 1)]
                if rng.random() < crossover_rate:
                    alpha = rng.uniform(0.0, 1.0, size=n_dim)
                    c1 = alpha * p1 + (1.0 - alpha) * p2
                    c2 = alpha * p2 + (1.0 - alpha) * p1
                else:
                    c1, c2 = p1.copy(), p2.copy()

                offspring[i] = c1
                if i + 1 < pop_size:
                    offspring[i + 1] = c2

            # Gaussian mutation
            mutation_mask = rng.random(size=(pop_size, n_dim)) < mutation_rate
            if np.any(mutation_mask):
                noise = rng.normal(0.0, 0.1 * span, size=(pop_size, n_dim))
                offspring = np.where(mutation_mask, offspring + noise, offspring)

            offspring = np.clip(offspring, lb, ub)

            if n_elite > 0:
                offspring[:n_elite] = elites

            population = offspring
            raw_fitness = np.array([fitness_fn(ind) for ind in population], dtype=float)
            internal_costs = sign * raw_fitness

            gen_best_idx = int(np.argmin(internal_costs))
            if internal_costs[gen_best_idx] < sign * best_fitness:
                best_fitness = float(raw_fitness[gen_best_idx])
                best_position = population[gen_best_idx].copy()

            history_best.append(best_fitness)
            history_mean.append(float(np.mean(raw_fitness)))
            history_diversity.append(compute_population_diversity(population, lb, ub))
            generations_done = gen

            if progress_callback is not None:
                progress_callback(gen, n_generations, best_fitness, best_position, history_best)

        return OptimizationResult(
            algorithm_key=self.key,
            algorithm_name=self.display_name,
            status=status,
            best_fitness=best_fitness,
            best_position=best_position,
            iterations_executed=generations_done,
            total_iterations=n_generations,
            history_best=history_best,
            history_mean=history_mean,
            history_diversity=history_diversity,
            objective="Maximize" if is_maximize else "Minimize",
            parameters=clean_params,
        )


class ParticleSwarmOptimizer(BaseOptimizer):
    key = "PSO"
    display_name = "PSO - Particle Swarm Optimization"

    @classmethod
    def get_parameter_specs(cls) -> List[ParameterSpec]:
        return [
            ParameterSpec(
                name="num_particles",
                label="Number of Particles:",
                param_type="int",
                default=30,
                min_val=2,
                max_val=10000,
                tooltip="Swarm size (number of particles exploring the search space, default: 30).",
            ),
            ParameterSpec(
                name="num_iterations",
                label="Number of Iterations:",
                param_type="int",
                default=100,
                min_val=1,
                max_val=100000,
                tooltip="Total number of swarm iterations to execute (default: 100).",
            ),
            ParameterSpec(
                name="inertia_weight",
                label="Inertia Weight (w):",
                param_type="float",
                default=0.7,
                min_val=0.0,
                max_val=5.0,
                step=0.05,
                decimals=3,
                tooltip="Inertia weight controlling momentum of particle velocity (default: 0.7).",
            ),
            ParameterSpec(
                name="cognitive_coeff",
                label="Cognitive Coefficient (c1):",
                param_type="float",
                default=1.5,
                min_val=0.0,
                max_val=10.0,
                step=0.1,
                decimals=3,
                tooltip="Personal attraction coefficient toward each particle's best position (default: 1.5).",
            ),
            ParameterSpec(
                name="social_coeff",
                label="Social Coefficient (c2):",
                param_type="float",
                default=1.5,
                min_val=0.0,
                max_val=10.0,
                step=0.1,
                decimals=3,
                tooltip="Social attraction coefficient toward the global best position (default: 1.5).",
            ),
            ParameterSpec(
                name="random_seed",
                label="Random Seed:",
                param_type="seed",
                default="42",
                tooltip="Integer seed for reproducibility (leave blank for random behavior).",
            ),
        ]

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], float],
        bounds: List[Tuple[float, float]],
        params: Dict[str, Any],
        objective: str = "Minimize",
        progress_callback: Optional[Callable[[int, int, float, np.ndarray, List[float]], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> OptimizationResult:
        clean_params = self.validate_parameters(params)
        n_particles: int = clean_params["num_particles"]
        n_iterations: int = clean_params["num_iterations"]
        w: float = clean_params["inertia_weight"]
        c1: float = clean_params["cognitive_coeff"]
        c2: float = clean_params["social_coeff"]
        seed: Optional[int] = clean_params["random_seed"]

        is_maximize = str(objective).strip().lower().startswith("max")
        sign = -1.0 if is_maximize else 1.0

        rng = np.random.default_rng(seed)
        n_dim = len(bounds)
        lb = np.array([b[0] for b in bounds], dtype=float)
        ub = np.array([b[1] for b in bounds], dtype=float)
        span = ub - lb
        v_max = 0.2 * span

        positions = rng.uniform(lb, ub, size=(n_particles, n_dim))
        velocities = rng.uniform(-v_max, v_max, size=(n_particles, n_dim))

        raw_fitness = np.array([fitness_fn(pos) for pos in positions], dtype=float)
        internal_costs = sign * raw_fitness

        pbest_positions = positions.copy()
        pbest_costs = internal_costs.copy()

        gbest_idx = int(np.argmin(pbest_costs))
        gbest_position = pbest_positions[gbest_idx].copy()
        gbest_cost = float(pbest_costs[gbest_idx])
        best_fitness = float(raw_fitness[gbest_idx])

        history_best: List[float] = []
        history_mean: List[float] = []
        history_diversity: List[float] = []
        iterations_done = 0
        status = "Completed"

        for it in range(1, n_iterations + 1):
            if cancel_check is not None and cancel_check():
                status = "Cancelled"
                break

            r1 = rng.random(size=(n_particles, n_dim))
            r2 = rng.random(size=(n_particles, n_dim))

            velocities = (
                w * velocities
                + c1 * r1 * (pbest_positions - positions)
                + c2 * r2 * (gbest_position - positions)
            )
            velocities = np.clip(velocities, -v_max, v_max)
            positions = np.clip(positions + velocities, lb, ub)

            raw_fitness = np.array([fitness_fn(pos) for pos in positions], dtype=float)
            internal_costs = sign * raw_fitness

            improved = internal_costs < pbest_costs
            pbest_positions[improved] = positions[improved]
            pbest_costs[improved] = internal_costs[improved]

            iter_best_idx = int(np.argmin(pbest_costs))
            if pbest_costs[iter_best_idx] < gbest_cost:
                gbest_cost = float(pbest_costs[iter_best_idx])
                gbest_position = pbest_positions[iter_best_idx].copy()
                best_fitness = float(sign * gbest_cost)

            history_best.append(best_fitness)
            history_mean.append(float(np.mean(raw_fitness)))
            history_diversity.append(compute_population_diversity(positions, lb, ub))
            iterations_done = it

            if progress_callback is not None:
                progress_callback(it, n_iterations, best_fitness, gbest_position, history_best)

        return OptimizationResult(
            algorithm_key=self.key,
            algorithm_name=self.display_name,
            status=status,
            best_fitness=best_fitness,
            best_position=gbest_position,
            iterations_executed=iterations_done,
            total_iterations=n_iterations,
            history_best=history_best,
            history_mean=history_mean,
            history_diversity=history_diversity,
            objective="Maximize" if is_maximize else "Minimize",
            parameters=clean_params,
        )


# Extensible Registry: adding DE, SA, or CMA-ES in the future only requires registering a new BaseOptimizer subclass here.
OPTIMIZER_REGISTRY: Dict[str, type[BaseOptimizer]] = {
    GeneticAlgorithmOptimizer.display_name: GeneticAlgorithmOptimizer,
    ParticleSwarmOptimizer.display_name: ParticleSwarmOptimizer,
}


def get_optimizer(algorithm_display_name: str) -> BaseOptimizer:
    if not algorithm_display_name or algorithm_display_name not in OPTIMIZER_REGISTRY:
        raise InvalidParameterError("No valid optimization algorithm selected.")
    return OPTIMIZER_REGISTRY[algorithm_display_name]()

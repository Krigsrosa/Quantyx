import pandas as pd
import numpy as np

def generate_dummy_data(rows=100000, cols=20, file_path="dummy_data.csv"):
    """Generates dummy industrial data for testing pyTab."""
    print(f"Generating {rows} rows of dummy data...")
    data = {}
    
    # Process parameters
    data["Temperature"] = np.random.normal(loc=150, scale=10, size=rows)
    data["Pressure"] = np.random.normal(loc=5, scale=0.5, size=rows)
    data["Flow_Rate"] = np.random.uniform(low=10, high=50, size=rows)
    data["Vibration"] = np.random.exponential(scale=1.5, size=rows)
    
    # Target variable (Yield) with some correlation to Temperature and Pressure
    data["Yield"] = (
        80 + 
        (data["Temperature"] - 150) * 0.5 - 
        (data["Pressure"] - 5) * 2 + 
        np.random.normal(0, 2, size=rows)
    )
    
    # Categorical
    data["Machine_ID"] = np.random.choice(["M-01", "M-02", "M-03", "M-04"], size=rows)
    data["Operator"] = np.random.choice(["Alice", "Bob", "Charlie"], size=rows)
    
    # Add random numeric columns
    for i in range(cols - 7):
        data[f"Sensor_{i+1:02d}"] = np.random.randn(rows) * (i + 1)
        
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    generate_dummy_data()

import os
import sys
import shutil

def get_app_data_dir():
    # Use roaming appdata on Windows
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = os.path.expanduser('~')
    
    quantyx_dir = os.path.join(appdata, 'Quantyx')
    if not os.path.exists(quantyx_dir):
        os.makedirs(quantyx_dir)
        
    return quantyx_dir

def get_templates_dir():
    templates_dir = os.path.join(get_app_data_dir(), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        # Copy default template if running from PyInstaller
        if hasattr(sys, '_MEIPASS'):
            default_tpl = os.path.join(sys._MEIPASS, 'template', 'GlobalRD_Template.pptx')
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_tpl = os.path.join(base_path, 'template', 'GlobalRD_Template.pptx')
            
        if os.path.exists(default_tpl):
            dest_tpl = os.path.join(templates_dir, 'GlobalRD_Template.pptx')
            if not os.path.exists(dest_tpl):
                shutil.copy2(default_tpl, dest_tpl)
                
    return templates_dir

import json

def get_settings_file():
    return os.path.join(get_app_data_dir(), 'settings.json')

def load_settings():
    settings_file = get_settings_file()
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_settings(settings):
    settings_file = get_settings_file()
    try:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
    except:
        pass

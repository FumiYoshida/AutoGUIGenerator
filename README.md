<p align="center"><img width=12.5% src="/media/logo.png"></p>
<p align="center"><img width=60% src="/media/name.png"></p>

<p align="center">
 <img src="https://img.shields.io/badge/python-v3.9+-blue.svg">
 <img src="https://img.shields.io/badge/contributions-welcome-orange.svg">
 <a href="https://opensource.org/licenses/MIT">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg">
 </a>
</p>

## Basic Overview
A library for concise GUI creation based on tkinter.

## Last Stable Release
```bash
pip install git+https://github.com/FumiYoshida/AutoGUIGenerator
```

## Tutorial

### Basic Example
You can create a rough outline as follows.
```python
from guigen import Application

class YourClass:
    def __init__(self):
        # initialize gui
        self.app = Application(self.main)
        
        # add figure to GUI if you need
        self.app.add_figure('your_figure_name', self.init_anim, self.update_anim)
        
        # add button to GUI if you need
        self.app.button(self.some_function_fire_at_push_of_button)
        
        # start tkinter mainloop
        self.app.start()
        
    def main(self):
        # define your function to execute periodically
        pass
        
    def init_anim(self):
        # define your function to initialize figure
        pass
        
    def update_anim(self):
        # define your function to update figure
        pass
        
    def some_function_fire_at_push_of_button(self):
        # define your function(s) to fire when button(s) is (are) pressed
        pass
```

### Getting float from GUI
If you need to get the float from the GUI, you can write the following to get it directly from the GUI.

```python
# in the main function above
float_entered_by_user_via_GUI = self.app.get_float('name_of_float', MIN_VALUE_OF_SLIDER, MAX_VALUE_OF_SLIDER, DEFAULT_VALUE)
```
A slider is automatically added to the GUI.

### Getting bool from GUI
If you need to get the bool from the GUI, you can write the following to get it directly from the GUI.

```python
# in the main function above
bool_entered_by_user_via_GUI = self.app.get_bool('name_of_bool', DEFAULT_VALUE)
```
A toggle button is automatically added to the GUI.

## Further Examples
- [metronome](test/metronome.ipynb)
<img width=60% src="/media/metronome_example.png">

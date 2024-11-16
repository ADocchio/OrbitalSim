from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, \
    QPushButton, QLabel, QDialog, QListWidget, QFrame, QComboBox, QCheckBox, QDoubleSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import orbital_state as os
import plotting as pt
import spiceypy as spice
import planet_data as pd
from OrbitCode.plotting import plot_orbits

#Style
STYLE = """
            /* Main Window and Dialog Background */
            QMainWindow, QDialog {
                background-color: #1C1B29;
            }

            /* Text Color and Font */
            QLabel {
                color: #C5C8FA;
                font-size: 16px;
            }

            /* Buttons */
            QPushButton {
                background-color: #3C3F58;
                border: 2px solid #6C6CE4;
                border-radius: 8px;
                padding: 8px;
                color: #C5C8FA;
            }

            QPushButton:hover {
                background-color: #5A5E82;
                border-color: #8A8AD9;
            }

            QPushButton:pressed {
                background-color: #32354A;
                border-color: #4B4B89;
            }

            /* Input Fields - QLineEdit, QDoubleSpinBox, and QComboBox */
            QLineEdit, QDoubleSpinBox, QComboBox {
                background-color: #2C2E41;
                border: 1px solid #6C6CE4;
                border-radius: 5px;
                color: #C5C8FA;
                padding: 4px;
            }

            /* List Widget */
            QListWidget {
                background-color: #2C2E41;
                border: 1px solid #6C6CE4;
                color: #C5C8FA;
            }

            /* Checkboxes */
            QCheckBox {
                color: #C5C8FA;
            }

            /* Image Border Styling */
            QLabel[imageLabel="true"] {
                border: 2px solid #6C6CE4;
                border-radius: 5px;
            }
        """

# Initialize orbital elements for the ISS and GEO
KOE_ISS = [6731, 0.000216, 51.64, 65.34, 225.44, 0]
KOE_GEO = [42164, 0.0, 0.0, 0.0, 0.0, 0.0]

# Load SPICE kernel for planetary data
spice.furnsh('kernal.mk')

# Store all active orbits
orbits = {}

class PlotDisplay2D(QWidget):
    """Control and display the 2D Plots (Groundtracks and Data)"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        self.drop_down = QComboBox()
        self.drop_down.addItem("Ground Track")
        self.drop_down.addItem("Variable Graphs")
        self.drop_down.currentIndexChanged.connect(self.dropdown_change)
        self.plot = Plot(self.main_window, pt.plot_groundtracks)

        # No orbits so nothing to display
        self.drop_down.setDisabled(True)

        layout.addWidget(self.drop_down)
        layout.addWidget(self.plot)
        self.setLayout(layout)

    # Logic for when dropdown menu is changed
    def dropdown_change(self):
        # Current index of dropdown menu
        index = self.drop_down.currentIndex()

        self.main_window.stop_animations()
        self.main_window.update_3d_plot(pt.plot_orbits)
        if index == 0:
            self.main_window.update_2d_plot(pt.plot_groundtracks)
        elif index == 1 and len(orbits) != 0:
            self.main_window.update_2d_plot(pt.plot_state_space, state_space= True)



class OrbitalElementDisplay(QWidget):
    """Displays orbital elements in a form layout."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QFormLayout()
        title = QLabel("Orbit Initial Conditions", self)
        title.setAlignment(Qt.AlignCenter)
        layout.addRow(title)
        layout.addRow(QLabel("", self))

        # Define orbital element fields
        self.values = [QLineEdit(self) for _ in range(9)]
        self.labels = ["Semi-Major Axis [km]:", "Eccentricity:",
                       "Inclination [Degrees]:", "Ascending Node [Degrees]:",
                       "Argument of Periapsis [Degrees]:", "True Anomaly [Degrees]:",
                       "Mass [kg]:", "Reflective Area [m^2]:", "Coefficient of Reflection:"]

        for line_edit in self.values:
            line_edit.setDisabled(True)

        for i, label_text in enumerate(self.labels):
            layout.addRow(QLabel(label_text), self.values[i])

        self.setLayout(layout)

    def display_values(self, orbit):
        for i, value in enumerate(self.values):
            value.setText(str(orbit.info[i]))

    def clear_values(self):
        for value in self.values:
            value.setText('')


class CreateOrbitDialog(QDialog):
    """Dialog for creating a new orbit."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("New Orbit")
        self.setGeometry(100, 100, 300, 400)
        self.setStyleSheet(STYLE)

        # Orbit specific args
        self.args = {
        'Mass': 1,  # kg
        'Asrp': 1,  # m^2
        'Cr': 1,  #
        }

        # Title Label
        title = QLabel("Keplerian Elements (Km & Degrees) & Satellite Information", self)
        title.setAlignment(Qt.AlignCenter)

        # Form Layout for orbit parameters
        self.form_layout = QFormLayout()
        self.inputs = [QLineEdit(self) for _ in range(10)]
        self.labels = ["Orbit Name:", "Semi-Major Axis [km]:", "Eccentricity:",
                       "Inclination [Degrees]:", "Ascending Node [Degrees]:",
                       "Argument of Periapsis [Degrees]:", "True Anomaly [Degrees]:",
                       "Mass [kg]:", "Reflective Area [m^2]:", "Coefficient of Reflection:"]

        # Adding labels and input fields to the form
        for i, label_text in enumerate(self.labels):
            self.form_layout.addRow(QLabel(label_text), self.inputs[i])

        # Set default values for semi-major axis and other elements
        self.inputs[1].setText(str(pd.Earth['radius'] + 1000))
        for i in range(2, 7):
            self.inputs[i].setText('0')

        # Set default values for Mass, Cr, and Asrp
        for i in range(7, 10):
            self.inputs[i].setText('1')

        # Hover tooltip for name
        self.inputs[0].setToolTip("Type 'ISS' or 'Geo' to use preset")

        # Orbit Propagate Button
        self.create_button = QPushButton("Propagate Orbit", self)
        self.create_button.clicked.connect(self.create_orbit)

        # Orbit elements diagram image
        image = QLabel(self)
        pixmap = QPixmap("Img/orbital-elements.png")
        image.setPixmap(pixmap)

        # Layout Setup
        form_widget = QWidget()
        form_widget.setMinimumSize(400, 400)
        form_widget.setLayout(self.form_layout)

        main_layout = QHBoxLayout()
        main_layout.addWidget(form_widget)
        main_layout.addWidget(image)

        final_layout = QVBoxLayout()
        final_layout.addWidget(title)
        final_layout.addLayout(main_layout)
        final_layout.addWidget(self.create_button)

        self.setLayout(final_layout)

    # Create orbit, and add to orbit list
    def create_orbit(self):
        inputs = [field.text() for field in self.inputs]

        # Validation
        valid, message = self.validate_inputs(inputs)
        if not valid:
            self.main_window.showAlert(message)
            return

        # Create new orbit if the name is unique
        orbit_name = inputs[0]

        # Check if user inputs any predefined orbits
        if orbits.get(orbit_name) is None:
            if orbit_name.startswith("ISS"):
                inputs[1:] = KOE_ISS + inputs[7:10]
            elif orbit_name.startswith("Geo"):
                inputs[1:] = KOE_GEO + inputs[7:10]

            # set orbit specific simulation arguments
            self.args['Mass'] = float(inputs[7])
            self.args['Asrp'] = float(inputs[8])
            self.args['Cr'] = float(inputs[9])

            new_orbit = os.OrbitalState(list(map(float, inputs[1:7])), self.args | self.main_window.simulation_args())
            new_orbit.propagate_orbit()
            new_orbit.latlongs()
            new_orbit.koe_propagation()
            orbits[orbit_name] = new_orbit

            # Update graphs and orbit list
            self.main_window.reset_gui()
            self.main_window.enable_dropdown(False)
            self.main_window.parameter_display.orbit_list.addItem(orbit_name)
            self.close()

    # Make inputs are valid
    def validate_inputs(self, inputs):

        # Check range of inputs and type
        for i, text in enumerate(inputs):
            try:
                value = float(text)
                if i == 1 and value <= pd.Earth['radius']:
                    return False, "Semi-major axis is too close to Earth's radius."
                elif i == 2 and not (0.0 <= value <= 1.0):
                    return False, "Eccentricity must be between 0 and 1."
                elif i in {3, 4, 5, 6} and not (0.0 <= value <= 360.0):
                    return False, f"{self.labels[i]} must be between 0 and 360 degrees."
            except ValueError:
                if i != 0:
                    return False, f"{self.labels[i]} is not a valid number."

        # Check for collisions
        if pd.Earth['radius'] >= float(inputs[1]) * (1 - float(inputs[2])):
            return False, "Orbit fly's to close to orbited body"

        return True, ""

class ParameterDisplay(QWidget):
    """Displays and manages the list of plotted orbits."""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout()
        title = QLabel("Orbits")
        self.orbit_list = QListWidget()
        self.orbit_list.setMinimumSize(150, 100)
        self.orbit_list.itemSelectionChanged.connect(self.main_window.element_display_selected)

        # Orbit Controls
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Orbit")
        self.delete_button = QPushButton("Delete Orbit")
        self.create_button.clicked.connect(self.create_orbit)
        self.delete_button.clicked.connect(self.delete_orbit)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.delete_button)

        # Animation and Time Settings
        settings_layout = QFormLayout()
        self.animate_checkbox = QCheckBox("Animate")
        self.animate_checkbox.stateChanged.connect(self.on_animate)
        self.timespan_input = QDoubleSpinBox()
        self.timespan_input.setPrefix("Timespan (days): ")
        self.timespan_input.setRange(0.01, 365.0)
        self.timespan_input.setValue(1.0)

        self.timestep_input = QDoubleSpinBox()
        self.timestep_input.setPrefix("Timestep (s): ")
        self.timestep_input.setRange(10, 86400)
        self.timestep_input.setValue(60)
        self.timespan_input.editingFinished.connect(self.focus_lost)
        self.timestep_input.editingFinished.connect(self.focus_lost)

        # Perturbation Settings
        self.j2_checkbox = QCheckBox("J2 Pert")
        self.j2_checkbox.stateChanged.connect(self.focus_lost)

        self.solar_checkbox = QCheckBox("Solar Pressure")
        self.solar_checkbox.stateChanged.connect(self.focus_lost)

        self.lunar_checkbox = QCheckBox("Lunar Gravity")
        self.lunar_checkbox.stateChanged.connect(self.focus_lost)

        # Layout
        settings_box = QHBoxLayout()
        settings_box.addWidget(self.animate_checkbox)
        settings_box.addWidget(self.j2_checkbox)
        settings_box.addWidget(self.solar_checkbox)
        settings_box.addWidget(self.lunar_checkbox)

        settings_layout.addRow(settings_box)
        settings_layout.addRow(self.timespan_input)
        settings_layout.addRow(self.timestep_input)

        layout.addWidget(title)
        layout.addWidget(self.orbit_list)
        layout.addLayout(button_layout)
        layout.addLayout(settings_layout)

        self.setLayout(layout)

        # Args shared by every orbit
        self.args = {
            'perturbations':
                {
                    'j2': False,
                    'solar': False,
                    'lunar': False
                },

            'startDate': '2020-01-01',  # J2000
            'tSpan': 86400,  # One Day
            'dt': 60.0,  # Every minute
        }

    #currently selected item
    def current_item(self):
        return self.orbit_list.currentItem()

    # orbit creation dialog launched
    def create_orbit(self):
        self.main_window.stop_animations()
        orbit = CreateOrbitDialog(self.main_window)
        orbit.exec_()

    # orbit removed from simulation
    def delete_orbit(self):
        item = self.orbit_list.currentRow()
        if item != -1:
            orbits.pop(self.orbit_list.currentItem().text())
            self.orbit_list.takeItem(item)
            self.main_window.reset_gui()
            self.main_window.enable_dropdown(True)

    # Update simulations when the parameters are changed
    def focus_lost(self):
        self.main_window.stop_animations()

        # Validate input fields for timespan and timestep
        try:
            time_span_value = self.timespan_input.value()
            time_step_value = self.timestep_input.value()
            if time_span_value <= 0 or time_step_value <= 0:
                raise ValueError("Time span and time step must be greater than zero.")
        except ValueError:
            self.main_window.showAlert("Simulation parameters out of bounds.")
            return

        # Update args dictionary
        if time_span_value != self.args['tSpan'] / (86400):  # Convert to days for comparison
            self.args['tSpan'] = time_span_value * 86400  # Convert days to seconds
        if time_step_value != self.args['dt']:
            self.args['dt'] = time_step_value  # Update timestep in seconds

        if self.j2_checkbox.isChecked(): # Update J2
            self.args['perturbations']['j2'] = True
        else:
            self.args['perturbations']['j2'] = False

        if self.solar_checkbox.isChecked(): # Update Solar
            self.args['perturbations']['solar'] = True
        else:
            self.args['perturbations']['solar'] = False

        if self.lunar_checkbox.isChecked(): # Update Lunar
            self.args['perturbations']['lunar'] = True
        else:
            self.args['perturbations']['lunar'] = False

        # Update plots with re-simulation
        self.main_window.update_3d_plot(pt.plot_orbits, re_simulate=True)
        self.main_window.update_2d_plot(pt.plot_groundtracks, re_simulate=True)

        # If "Variable Graphs" is selected in the dropdown, update state space plot
        if len(orbits) != 0 and self.main_window.plot_display_2d.drop_down.currentIndex() == 1:
            self.main_window.update_2d_plot(pt.plot_state_space, state_space=True)

    # Handles responses to user clicking or unchecking the checkbox
    def on_animate(self, state):
        if self.animate_checkbox.isChecked():
            if len(orbits.keys()) <= 0:
                self.main_window.showAlert("No orbits to animate")
                self.animate_checkbox.setChecked(False)
                return
            else:
                self.main_window.start_animations()
        else:
            self.main_window.stop_animations()
            self.main_window.reset_gui()


class Plot(QWidget):
    """Matplotlib canvas handler"""
    def __init__(self, main_window, plotting_function):
        super().__init__()
        self.main_window = main_window
        self.setMinimumSize(610, 410)
        self.plotting_function = plotting_function
        self.canvas = PlotCanvas(self.plotting_function(orbits, args=self.main_window.simulation_args()))

        # Create Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.animation = None  # Placeholder for animation object

    # Call the provided animation function to start the FuncAnimation
    def start_animation(self, animation_function):
        anim, fig = animation_function(orbits, False)
        self.animation = anim
        self.change_plot(fig)

    # Stop animation
    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()

    #Redraw the canvas
    def change_plot(self, fig):
        # Remove old canvas and clear previous animation if it exists
        self.canvas.wipe()
        plt.close(self.canvas.fig)
        self.layout.removeWidget(self.canvas)

        # Assign new canvas
        self.canvas = PlotCanvas(fig)
        self.layout.addWidget(self.canvas)

class PlotCanvas(FigureCanvas):
    """Matplotlib canvas object"""
    def __init__(self, fig, parent=None):
        super(PlotCanvas, self).__init__(fig)
        self.fig = fig  # Store the figure for later use
        self.setParent(parent)

    # Clear the figure and redraw the canvas
    def wipe(self):
        self.fig.clear()  # Clear the current figure
        self.draw()  # Redraw the canvas to reflect the clearing



class Alert(QDialog):
    """Used to display alerts to the user"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Alert!")
        self.setGeometry(50, 50, 100, 100)

        # Alert messages
        self.label = QLabel()
        self.label.setText("")

        # Alert button
        button = QPushButton()
        button.clicked.connect(self.end)
        button.setText("Close")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(button)
        self.setLayout(layout)

    # Send an alert out to the user
    def setAlert(self, message):
        self.label.setText(message)

    # Close the alert popup
    def end(self):
        self.close()

class MainWindow(QMainWindow):
    """Main application window with layouts and central widget."""
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("Orbit Simulation")
        self.setGeometry(100, 100, 1600, 1200)
        self.alert = Alert(self)

        # Apply the stylesheet
        # Apply the stylesheet in MainWindow __init__
        self.setStyleSheet(STYLE)

        # Create the central widget and Main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create lower right layout
        lower_right_layout = QHBoxLayout()
        self.orbital_element_display = OrbitalElementDisplay(self)
        self.parameter_display = ParameterDisplay(self)

        # Create upper right layout
        upper_right_layout = QHBoxLayout()
        self.plot_display_2d = PlotDisplay2D(self)
        upper_right_layout.addWidget(self.plot_display_2d)

        lower_right_layout.addWidget(self.orbital_element_display)
        lower_right_layout.addWidget(self.parameter_display)

        # Create right display
        right_layout = QVBoxLayout()
        right_layout.addLayout(upper_right_layout)
        right_layout.addLayout(lower_right_layout)

        # Create left display
        left_layout = QHBoxLayout()
        self.plot_display_3d = Plot(self, plot_orbits)
        left_layout.addWidget(self.plot_display_3d)

        # Add layouts to the main layout
        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        main_layout.addLayout(layout)

    # Update 2d plot
    def update_2d_plot(self, plotting_function, re_simulate = False, state_space = False):
        if state_space:
            orbit = self.parameter_display.current_item().text()
            self.plot_display_2d.plot.change_plot(plotting_function(orbits[orbit], re_simulate, self.simulation_args()))
        else:
            self.plot_display_2d.plot.change_plot(plotting_function(orbits, re_simulate, self.simulation_args()))

    # Update 3d plot
    def update_3d_plot(self, plotting_function, re_simulate = False):
        self.plot_display_3d.change_plot(plotting_function(orbits, re_simulate, self.simulation_args()))

    # Controls logic for changing UI when new orbit is selected
    def element_display_selected(self):
        self.stop_animations()
        if len(orbits) != 0:
            orbit_name = self.parameter_display.current_item().text()
            self.orbital_element_display.display_values(orbits[orbit_name])
            if self.plot_display_2d.drop_down.currentIndex() == 1:
                self.update_2d_plot(pt.plot_state_space, state_space=True)
        else:
            self.orbital_element_display.clear_values()

    def start_animations(self):
        self.reset_gui()
        self.plot_display_2d.plot.start_animation(pt.animate_groundtracks)
        self.plot_display_3d.start_animation(pt.animate_Orbits)

    def stop_animations(self):
        if self.parameter_display.animate_checkbox.isChecked():
            self.plot_display_2d.plot.stop_animation()
            self.plot_display_3d.stop_animation()
            self.parameter_display.animate_checkbox.setChecked(False)

    # Resets the dropdown to ground tracks and re-plots all plots in presses
    def reset_gui(self):
        if self.plot_display_2d.drop_down.currentIndex() == 0:
            self.update_3d_plot(plot_orbits)
            self.update_2d_plot(pt.plot_groundtracks)
        else:
            self.plot_display_2d.drop_down.setCurrentIndex(0)

    # allows for enabling or disabling the dropdown menu
    def enable_dropdown(self, value):
        self.plot_display_2d.drop_down.setDisabled(value)

    # Gets the simulation wide orbital arguments
    def simulation_args(self):
        return self.parameter_display.args

    # Calls an alert to be sent to the user
    def showAlert(self, message):
        self.alert.setAlert(message)
        self.alert.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

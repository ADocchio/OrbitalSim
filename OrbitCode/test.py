from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, \
    QLabel, QComboBox, QListWidget, QCheckBox, QDoubleSpinBox, QSplitter
import sys


class OrbitSimulationApp(QWidget):
    def __init__(self):
        super().__init__()

        # MAIN LAYOUT - Uses QSplitter for resizable sections
        main_layout = QVBoxLayout(self)

        # TOP LAYOUT - Contains the Simulation and Ground Track Views
        top_splitter = QSplitter()

        # Orbital Simulation Graph
        self.simulation_view = QLabel("Orbital Simulation View")
        self.simulation_view.setFixedSize(500, 400)  # Replace with canvas for the simulation graph
        self.simulation_view.setStyleSheet("background-color: #222; color: white;")

        # Ground Map View
        self.ground_track_view = QLabel("Ground Map View")
        self.ground_track_view.setFixedSize(500, 400)  # Replace with canvas for the ground map graph
        self.ground_track_view.setStyleSheet("background-color: #222; color: white;")

        # Add to splitter for top layout
        top_splitter.addWidget(self.simulation_view)
        top_splitter.addWidget(self.ground_track_view)
        main_layout.addWidget(top_splitter)

        # BOTTOM LAYOUT - Contains Orbit List, Controls, and Kepler Elements
        bottom_layout = QHBoxLayout()

        # LEFT BOTTOM - Orbit List and Controls
        left_bottom_layout = QVBoxLayout()

        # Orbit List
        orbit_list_label = QLabel("Orbits")
        self.orbit_list = QListWidget()
        self.orbit_list.setFixedSize(250, 200)

        # Orbit Controls
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Orbit")
        self.delete_button = QPushButton("Delete Orbit")
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.delete_button)

        # Add Orbit List and Controls
        left_bottom_layout.addWidget(orbit_list_label)
        left_bottom_layout.addWidget(self.orbit_list)
        left_bottom_layout.addLayout(button_layout)

        # Animation and Time Settings
        settings_layout = QFormLayout()
        self.animate_checkbox = QCheckBox("Animate")
        self.timespan_input = QDoubleSpinBox()
        self.timespan_input.setPrefix("Timespan (days): ")
        self.timespan_input.setRange(0.1, 365.0)
        self.timespan_input.setValue(1.0)

        self.timestep_input = QDoubleSpinBox()
        self.timestep_input.setPrefix("Timestep (s): ")
        self.timestep_input.setRange(1, 86400)
        self.timestep_input.setValue(60)

        settings_layout.addRow(self.animate_checkbox)
        settings_layout.addRow(self.timespan_input)
        settings_layout.addRow(self.timestep_input)

        left_bottom_layout.addLayout(settings_layout)
        bottom_layout.addLayout(left_bottom_layout)

        # RIGHT BOTTOM - Keplerian Elements Display
        kepler_layout = QVBoxLayout()
        kepler_label = QLabel("Keplerian Orbital Elements")
        kepler_layout.addWidget(kepler_label)

        kepler_elements_layout = QFormLayout()
        self.eccentricity_label = QLineEdit()
        self.eccentricity_label.setReadOnly(True)
        self.semi_major_axis_label = QLineEdit()
        self.semi_major_axis_label.setReadOnly(True)
        self.inclination_label = QLineEdit()
        self.inclination_label.setReadOnly(True)
        self.ascending_node_label = QLineEdit()
        self.ascending_node_label.setReadOnly(True)
        self.argument_of_periapsis_label = QLineEdit()
        self.argument_of_periapsis_label.setReadOnly(True)
        self.true_anomaly_label = QLineEdit()
        self.true_anomaly_label.setReadOnly(True)

        kepler_elements_layout.addRow("Eccentricity:", self.eccentricity_label)
        kepler_elements_layout.addRow("Semi-Major Axis:", self.semi_major_axis_label)
        kepler_elements_layout.addRow("Inclination:", self.inclination_label)
        kepler_elements_layout.addRow("Ascending Node:", self.ascending_node_label)
        kepler_elements_layout.addRow("Argument of Periapsis:", self.argument_of_periapsis_label)
        kepler_elements_layout.addRow("True Anomaly:", self.true_anomaly_label)

        kepler_layout.addLayout(kepler_elements_layout)
        bottom_layout.addLayout(kepler_layout)

        # Add bottom layout to main layout
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.setWindowTitle("Orbital Simulation Program")
        self.setGeometry(100, 100, 1100, 800)


# Run the application
app = QApplication(sys.argv)
window = OrbitSimulationApp()
window.show()
sys.exit(app.exec_())

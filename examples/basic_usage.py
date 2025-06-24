"""
Basic usage example for T-GUI.

This example demonstrates how to create a simple T-GUI application
with a viewer and some sample data.
"""

import numpy as np
import t_gui


def main():
    """Main function demonstrating basic T-GUI usage."""
    
    # Create a viewer
    viewer = t_gui.make_viewer()
    
    # Add some sample image data
    image_data = np.random.random((100, 100))
    viewer.add_image(image_data, name="Random Image", colormap='viridis')
    
    # Add some sample points data
    points_data = np.random.random((50, 2)) * 100
    viewer.add_points(points_data, name="Random Points", size=5, face_color='red')
    
    # Add another image layer
    gradient = np.linspace(0, 1, 100)
    gradient_2d = np.outer(gradient, gradient)
    viewer.add_image(gradient_2d, name="Gradient", colormap='plasma', opacity=0.7)
    
    # Launch the application
    t_gui.run()


def create_custom_viewer():
    """Example of creating a custom viewer with specific settings."""
    
    # Create viewer with custom title
    viewer = t_gui.Viewer(title="My Custom Viewer")
    
    # Add multiple layers
    for i in range(3):
        data = np.random.random((50, 50)) * (i + 1)
        viewer.add_image(data, name=f"Layer {i+1}")
    
    # Create main window and set the viewer
    window = t_gui.MainWindow()
    window.set_viewer(viewer)
    
    # Show the window
    window.show()
    
    return window


def demonstrate_events():
    """Demonstrate the event system."""
    
    viewer = t_gui.make_viewer()
    
    # Connect to viewer events
    def on_layer_added(event):
        layer = event.data['layer']
        print(f"Layer added: {layer.name}")
    
    def on_layer_removed(event):
        layer = event.data['layer']
        print(f"Layer removed: {layer.name}")
    
    viewer.connect('layer_added', on_layer_added)
    viewer.connect('layer_removed', on_layer_removed)
    
    # Add and remove layers to see events
    layer1 = viewer.add_image(np.random.random((50, 50)), name="Test Layer 1")
    layer2 = viewer.add_image(np.random.random((50, 50)), name="Test Layer 2")
    
    viewer.remove_layer(layer1)
    
    return viewer


def demonstrate_settings():
    """Demonstrate the settings system."""
    
    from t_gui.settings import get_settings
    
    settings = get_settings()
    
    # Get current theme
    theme = settings.get('appearance.theme')
    print(f"Current theme: {theme}")
    
    # Change theme
    settings.set('appearance.theme', 'light')
    
    # Get all appearance settings
    appearance = settings.get('appearance')
    print(f"Appearance settings: {appearance}")
    
    # Reset to defaults
    settings.reset_to_defaults()


if __name__ == "__main__":
    # Run the basic example
    main()
    
    # Uncomment to try other examples:
    # window = create_custom_viewer()
    # viewer = demonstrate_events()
    # demonstrate_settings()

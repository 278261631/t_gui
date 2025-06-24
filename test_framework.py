#!/usr/bin/env python3
"""
Test script for T-GUI framework.

This script tests the basic functionality of the T-GUI framework
to ensure everything is working correctly.
"""

import sys
import numpy as np

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        import t_gui
        print("✓ Main t_gui module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import t_gui: {e}")
        return False
    
    try:
        from t_gui.components.viewer import Viewer, Layer, ImageLayer, PointsLayer
        print("✓ Viewer components imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import viewer components: {e}")
        return False
    
    try:
        from t_gui.events import Event, EventEmitter, EventManager
        print("✓ Event system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import event system: {e}")
        return False
    
    try:
        from t_gui.plugins import PluginManager, hookspecs
        print("✓ Plugin system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import plugin system: {e}")
        return False
    
    try:
        from t_gui.settings import get_settings
        print("✓ Settings system imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import settings system: {e}")
        return False
    
    return True


def test_viewer():
    """Test viewer functionality."""
    print("\nTesting viewer functionality...")
    
    try:
        from t_gui.components.viewer import Viewer
        
        # Create viewer
        viewer = Viewer(title="Test Viewer")
        print("✓ Viewer created successfully")
        
        # Add image layer
        image_data = np.random.random((10, 10))
        image_layer = viewer.add_image(image_data, name="Test Image")
        print("✓ Image layer added successfully")
        
        # Add points layer
        points_data = np.random.random((5, 2)) * 10
        points_layer = viewer.add_points(points_data, name="Test Points")
        print("✓ Points layer added successfully")
        
        # Test layer management
        assert len(viewer.layers) == 2, "Expected 2 layers"
        assert viewer.active_layer is not None, "Expected active layer"
        print("✓ Layer management working correctly")
        
        # Test layer removal
        viewer.remove_layer(image_layer)
        assert len(viewer.layers) == 1, "Expected 1 layer after removal"
        print("✓ Layer removal working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Viewer test failed: {e}")
        return False


def test_events():
    """Test event system."""
    print("\nTesting event system...")
    
    try:
        from t_gui.events import EventEmitter, Event
        
        # Create event emitter
        emitter = EventEmitter()
        
        # Test event connection and emission
        events_received = []
        
        def event_handler(event):
            events_received.append(event)
        
        emitter.connect('test_event', event_handler)
        emitter.emit('test_event', data={'test': 'value'})
        
        assert len(events_received) == 1, "Expected 1 event"
        assert events_received[0].type == 'test_event', "Expected test_event type"
        print("✓ Event emission and handling working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Event system test failed: {e}")
        return False


def test_settings():
    """Test settings system."""
    print("\nTesting settings system...")
    
    try:
        from t_gui.settings import get_settings
        
        settings = get_settings()
        
        # Test getting default setting
        theme = settings.get('appearance.theme')
        assert theme is not None, "Expected theme setting"
        print("✓ Settings retrieval working correctly")
        
        # Test setting value
        settings.set('test.value', 'test_data', save=False)
        retrieved = settings.get('test.value')
        assert retrieved == 'test_data', "Expected test_data"
        print("✓ Settings modification working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Settings test failed: {e}")
        return False


def test_plugins():
    """Test plugin system."""
    print("\nTesting plugin system...")
    
    try:
        from t_gui.plugins import PluginManager
        
        plugin_manager = PluginManager()
        
        # Test plugin registry
        registry = plugin_manager.registry
        assert registry is not None, "Expected plugin registry"
        print("✓ Plugin manager created successfully")
        
        # Test plugin discovery (should not fail even with no plugins)
        plugin_manager.discover_plugins()
        print("✓ Plugin discovery working correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Plugin system test failed: {e}")
        return False


def test_qt_integration():
    """Test Qt integration (if available)."""
    print("\nTesting Qt integration...")
    
    try:
        from t_gui._qt import get_app, QT_BACKEND
        
        print(f"✓ Qt backend detected: {QT_BACKEND}")
        
        # Create Qt application
        app = get_app()
        assert app is not None, "Expected Qt application"
        print("✓ Qt application created successfully")
        
        # Test main window creation (without showing)
        from t_gui._qt.main_window import MainWindow
        window = MainWindow()
        assert window is not None, "Expected main window"
        print("✓ Main window created successfully")
        
        return True
        
    except ImportError as e:
        print(f"⚠ Qt not available: {e}")
        return True  # Not a failure if Qt is not installed
    except Exception as e:
        print(f"✗ Qt integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("T-GUI Framework Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_viewer,
        test_events,
        test_settings,
        test_plugins,
        test_qt_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! T-GUI framework is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

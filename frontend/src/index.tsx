import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import './App.css';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat'
import L from 'leaflet';
import { Provider } from 'react-redux';
import store from './store/store';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);

let DefaultIcon = L.icon({
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
});

L.Marker.prototype.options.icon = DefaultIcon;
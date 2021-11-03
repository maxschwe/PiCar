import "./App.css"
import Livestream from "./Components/Livestream"
import SensorDisplay from "./Components/SensorDisplay"
import MotorControl from "./Components/MotorControl"
import Terminal from "./Components/Terminal"

function App() {
  return (
    <div id="app">
      <div className="row">
        <Livestream />
        <SensorDisplay />
      </div>
      <div className="row">
        <MotorControl />
        <Terminal />
      </div>
    </div>
  );
}

export default App;

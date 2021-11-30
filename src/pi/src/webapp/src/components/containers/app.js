import React from "react";

import Livestream from "./livestream.js";
import Values from "./values.js";
import Control from "./controls.js";
import Terminal from "./terminal.js";

import "./styles.scss"

function App() {
    return (
        <>
        <h1>Pi Car</h1>
        <div id="container">
            <div className="wrapper-widget">
                <Livestream/>
            </div>
            <div className="wrapper-widget">
                <Values/>
            </div>
            <div className="wrapper-widget">
                <Control/>
            </div>
            <div className="wrapper-widget">
                <Terminal/>
            </div>
        </div>
        <div id="footer">
            <span id="copyright-text">&copy; Maximilian Schweiger</span>
            <a id="github" target="_blank" href="https://github.com/maxschwe/PiCar.git">Github</a>
        </div>
        </>
    )
}

export default App;
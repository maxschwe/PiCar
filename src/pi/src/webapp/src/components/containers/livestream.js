import React, { useState } from 'react';

function Livestream() {
    return (
        <div id="livestream" className="widget">
            <h3>Livestream:</h3>
            <div id="livestream-img-container">
                <img id="livestream-img" src="http://192.168.178.75:5000/livestream" alt="Livestream" />
            </div>
        </div>
    );
}

export default Livestream;
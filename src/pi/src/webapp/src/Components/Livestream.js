import React from 'react'
import "./../Styles/Livestream.css"

class Livestream extends React.Component {
    render(){
        return (<div id="livestream" className="app_container">
            <h1>Video Stream</h1>
            <img alt="Livestream Error" src="http://192.168.178.75:5000/livestream"></img>
        </div>)
    }
}

export default Livestream
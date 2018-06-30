//
// Author: jun10000 (https://github.com/jun10000)
//

class Pi
{
    static execute (mode)
    {
        let req = new XMLHttpRequest();
        req.open("GET", "cmd.py?mode=" + mode, true);
        req.send(null);
    }
}

class ControlBar
{
    static showOrHide()
    {
        let elem = document.getElementById("controlBar");
        elem.style.display = (elem.style.display === "") ? "initial" : "";
    }
}

class Audio
{
    static play (delay)
    {
        let proc = function ()
        {
            let elem_AudioController = document.getElementById("audioController");
            let elem_PlayAudioButton = document.getElementById("playAudioButton");

            if (elem_AudioController.paused) {
                elem_AudioController.play().then(function () {
                    elem_PlayAudioButton.innerText = "■";
                });
            }
        };
        setTimeout(proc, delay);
    }

    static stop (delay)
    {
        let proc = function ()
        {
            let elem_AudioController = document.getElementById("audioController");
            let elem_PlayAudioButton = document.getElementById("playAudioButton");

            if (!elem_AudioController.paused) {
                elem_AudioController.pause();
                elem_AudioController.currentTime = 0;
                elem_PlayAudioButton.innerText = "▶︎";
            }
        };
        setTimeout(proc, delay);
    }

    static playOrStop (delay)
    {
        let elem_AudioController = document.getElementById("audioController");
        if (elem_AudioController.paused) {
            Audio.play(delay);
        } else {
            Audio.stop(delay);
        }
    }
}

class Screen
{
    static toLighten ()
    {
        Pi.execute("to_lighten");
    }

    static toDarken ()
    {
        Pi.execute("to_darken");
    }

    static switchBrightness()
    {
        Pi.execute("switch_brightness");
    }
}

class Clock
{
    static start()
    {
        Clock.update();
        setTimeout(Clock.start, 1000);
    }

    static update()
    {
        let now = new Date();
        let hour = now.getHours();
        let hour_exp = (hour < 12) ? hour : hour - 12;
        let minute = now.getMinutes();
        let minute_exp = (minute >= 10) ? minute : "0" + minute;
        let second = now.getSeconds();
        let second_exp = (second >= 10) ? second : "0" + second;
        let am_pm = (hour < 12) ? "AM" : "PM";
        document.getElementById("clock").innerText =
            am_pm + " " + hour_exp + ":" + minute_exp + ":" + second_exp;
    }
}

//
// Class 'OnkyoRIListener's Variables
//
let OnkyoRIListener_RecentRecord = null;
let OnkyoRIListener_IsRequesting = false;

class OnkyoRIListener
{
    static start()
    {
        if (OnkyoRIListener_IsRequesting === false)
        {
            OnkyoRIListener_IsRequesting = true;
            OnkyoRIListener.getAndExecuteNewer();
        }
        setTimeout(OnkyoRIListener.start, 1000);
    }

    static getRecent()
    {
        let req = new XMLHttpRequest();
        req.open("GET", "cmd.py?mode=listen_recent_onkyori", true);
        req.onreadystatechange = function ()
        {
            if (req.readyState === 4 &&
                req.status === 200)
            {
                let result = JSON.parse(req.responseText);
                OnkyoRIListener_RecentRecord = result[0];
                OnkyoRIListener_IsRequesting = false;
            }
        };
        req.send(null);
    }

    static getAndExecuteNewer()
    {
        if (OnkyoRIListener_RecentRecord === null) {
            OnkyoRIListener.getRecent();
        } else {
            let id_min = OnkyoRIListener_RecentRecord["id"] + 1;

            let req = new XMLHttpRequest();
            req.open("GET", "cmd.py?mode=listen_onkyori&id_min=" + id_min, true);
            req.onreadystatechange = function ()
            {
                if (req.readyState === 4 && req.status === 200)
                {
                    let result = JSON.parse(req.responseText);
                    if (result.length > 0)
                    {
                        OnkyoRIListener_RecentRecord = result[result.length - 1];
                    }
                    for (let line of result)
                    {
                        switch (line["name"])
                        {
                            case "PowerOnTimer":
                                Screen.toLighten();
                                Audio.play(2500);
                                break;
                            case "PowerOff":
                                Screen.toDarken();
                                Audio.stop(0);
                                break;
                        }
                    }

                    OnkyoRIListener_IsRequesting = false;
                }
            };
            req.send(null);
        }
    }
}

//
// Entry Point
//

window.addEventListener("load", function ()
{
    document.getElementById("clockArea").addEventListener("click", function () { ControlBar.showOrHide(); });
    document.getElementById("playAudioButton").addEventListener("click", function () { Audio.playOrStop(0); });
    document.getElementById("switchBrightnessButton").addEventListener("click", function () { Screen.switchBrightness(); });

    Clock.start();
    OnkyoRIListener.start();
});

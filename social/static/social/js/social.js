let last_user_err = undefined;
(build_buttons = function () {


    function onclick(event) {
        /**
         * Mobile responsive system
         */
        let target = event.target
        while (target.querySelector('img') == undefined)
            target = target.parentNode
        messages_builder.set_current_user(target.querySelector('div>h2').innerHTML)

        document.querySelector('.chatnav').classList.add('hidden')
    }


    const users = document.querySelectorAll("div.user")
    for (let idx = 0; idx < users.length; idx ++) {
        users[idx].onclick = onclick
    }
    
    document.querySelector("div.chevron-right-container").onclick = (event) => {
        document.querySelector('.chatnav').classList.remove('hidden')
    }

    const challenge_buttons = document.querySelectorAll('.game-starter div>div>p')
    for (let idx = 0; idx < challenge_buttons.length; idx ++) {
        challenge_buttons[idx].onclick = (event) => {
            OPEN_WS_API.send('CHALLENGE: ' + messages_builder.get_current_user() + ': ' + event.target.innerHTML)

            const el = document.querySelector('.msg-input .game-starter')
            el.classList.toggle('hidden')
        }
    }

    const challenge_received_buttons = document.querySelectorAll('button.btn-chess-light[defi]')
    for (let idx = 0; idx < challenge_received_buttons.length; idx ++) {
        challenge_received_buttons[idx].onclick = (event) => {
            let target = event.target
            let defi = target.attributes['defi'].value
            OPEN_WS_API.send('ACCEPT: ' + defi)
        }
    }
})();

(start_socket = function () {
    const ws = new WebSocket("ws://" + document.location.hostname + ":" + document.location.port + "/ws/social/")
    let rstart = false;

    ws.onopen = function (event) {
        ws.send('GETDEFAULT')
    }

    ws.onclose = () => {if (rstart) start_socket}

    ws.onmessage = function (event) {
        let data = event.data
        let prot = data.split(': ')[0]

        if (prot == "MESSAGE") {
            let text = data.replace("MESSAGE: ", "")
            let user = text.split(': ')[0]
            let author = user.split('->')[0]
            let receiver = user.split('->')[1]
            text = text.replace(user + ': ', '')

            messages_builder.add_user_messages(author == username ? receiver : author, [[author, text]])
        } else if (prot == "MESSAGES") {
            let text = data.replace("MESSAGES: ", "")
            let json = JSON.parse(text)

            messages_builder.clear_messages()
            messages_builder.set_users(json)
        } else if (prot == 'USER_MESSAGES') {
            let text = data.replace("USER_MESSAGES: ", "")
            let user = text.split(': ')[0]
            text = text.replace(user + ': ', '')
            let json = JSON.parse(text)

            messages_builder.add_user_messages(user, json)
        } else if (prot == 'REDIRECT') {
            document.location.replace(data.replace("REDIRECT: ", ''))
        } else if (prot == 'INVIT') {
            let text = data.replace("INVIT: ", "")
            let user = text.split(': ')[0]
            let author = user.split('->')[0]
            let receiver = user.split('->')[1]
            let not_me = author == username ? receiver : author
            text = text.replace(user + ': ', '')

            if (messages_builder.load_user_messages(not_me)) {
                setTimeout( () => {
                    ws.onmessage(event)
                }, 333)
                return
            }

            if (author == username) {
                messages_builder.add_user_messages(not_me, [
                    [author, `Vous avez défié @${receiver} à jouer une partie`]
                ])
            } else {
                messages_builder.add_user_messages(not_me, [
                    [author, `@${author} vous a défié. <button id="accept" defi="${text}" class="btn btn-chess-light">Accepter le défi</button>`]
                ], safe=true)
            }
        } else if (prot == 'CLOSE_INVIT') {
            let text = data.replace("CLOSE_INVIT: ", "")
            let user = text.split(': ')[0]
            let author = user.split('->')[0]
            let receiver = user.split('->')[1]
            let not_me = author == username ? receiver : author
            text = text.replace(user + ': ', '')

            let msgtext = `@${author} vous a défié. <button id="accept" defi="${text}" class="btn btn-chess-light">Accepter le défi</button>`
            if (author == username)
                msgtext = `Vous avez défié @${receiver} à jouer une partie`
            
            messages_builder.remove_message(not_me, msgtext)
        } else if (prot == 'USERERROR') {
            last_user_err = data.replace("USERERROR: ", "")
            messages_builder._build()
        } else {
            console.log(data)
        }
    }

    OPEN_WS_API = {
        'send': (val) => {
            ws.send(val)
        }
    }
})();

(messages_builder = (function () {

    let users = {}
    let current_user = undefined

    function safify_string(str) {
        return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }
    function remove_html_balise (str) {
        let start = str.indexOf('<')
        let end = str.indexOf('>')

        while (start != -1 && end != -1) {
            str = str.substring(0,start) + str.substring(end+1)
            start = str.indexOf('<')
            end = str.indexOf('>')
        }

        return str
    }

    document.querySelector('.msg-area input').onkeydown = (event) => {
        if (event.key == 'Enter' || event.keyCode == 13) {
            let message = event.target.value
            if (message.trim() != '' && current_user != undefined && current_user.trim() != '') {
                OPEN_WS_API.send(`MESSAGE: ${current_user}: ${message}`)
                event.target.value = ''
                messages_builder.add_user_messages(current_user, [[username, message]])
            }
        }
    }

    return {
        'clear_messages': function () {
            users = {}
            messages_builder._build()
        },
        'get_current_user': function () {
            return current_user
        },
        'remove_message': function (user, text) {
            let idx = users[user].indexOf(text)
            users[user].splice(idx, 1)
            users[user][0] = users[user][users[user].length - 1][1]
            messages_builder._build()
        },
        'set_users': function (map) {
            // N * 2 map contains N users with name and last message
            for (let idx = 0; idx < map.length; idx ++) {
                users[map[idx][0]] = [safify_string(map[idx][1])]
            }

            if (map.length == 0) {
                current_user = undefined
            } else {
                current_user = map[0][0]
                if (users[current_user].length == 1)
                    OPEN_WS_API.send('GET_MESSAGES: ' + map[0][0])
            }
            
            messages_builder._build()
        },
        'load_user_messages': function () {
            if (users[current_user].length == 1)
                OPEN_WS_API.send('GET_MESSAGES: ' + current_user)
            return users[current_user].length == 1
        },
        'set_current_user': function (user) {
            current_user = user
            if (users[current_user].length == 1)
                OPEN_WS_API.send('GET_MESSAGES: ' + current_user)
            messages_builder._build()
        },
        'add_user_messages': function (user, messages, safe=false) {
            if (!Object.keys(users).includes(user)) {
                users[user] = ['']
                if (messages.length != 0)
                    users[user] = [safify_string(messages[0][1])]
            }
            if (messages.length != 0)
                users[user][0] = [safify_string(messages[0][1])]

            if (safe)
                if (messages.length != 0)
                    users[user][0] = [remove_html_balise(messages[0][1])]

            for (let idx = messages.length - 1; idx >= 0; idx --) {
                if (!safe)
                    users[user].push([messages[idx][0], safify_string(messages[idx][1])])
                else
                    users[user].push(messages[idx])
            }

            messages_builder._build()
        },
        '_build': function () {
            let users_keys = Object.keys(users)
            let html = `<h1>Discussions</h1>
                    <div class="input-container">
                        <input class="input" name="search" required>
                        <span></span>
                        <label class="inp-label">Ouvrir la conversation</label>
                    </div>${last_user_err != undefined ? `<p style="text-overflow: ellipsis; margin: 5px;">Une erreur est survenue avec l'utilisateur ${last_user_err}</p>` : ''}`
            for (let idx = 0; idx < users_keys.length; idx ++) {
                html += `<div class="user active">
                            <img class="online" src="/static/account/images/account_icon.png">
                            <div>
                                <h2>${users_keys[idx]}</h2>
                                <p>${users[users_keys[idx]][0]}</p>
                            </div>
                        </div>`
            }
            document.querySelector('.chatnav-users').innerHTML = html

            document.querySelector('.input-container input').onkeydown = (event) => {
                if (event.key == 'Enter' || event.keyCode == 13) {
                    OPEN_WS_API.send('GET_MESSAGES: ' + event.target.value)
                    event.target.value = ''
                }
            }

            document.querySelector('.col-1').innerHTML = ''

            if (current_user == undefined) {
                document.querySelector('.msg-area .msg-input').style.height = '0px';
                document.querySelector('.msg-area .msg-input').style.overflow = 'hidden';
                document.querySelector('.msg-area .msg-input').style.borderTop = 'none';
            } else {
                document.querySelector('.msg-area .msg-input').style.height = '';
                document.querySelector('.msg-area .msg-input').style.overflow = '';
                document.querySelector('.msg-area .msg-input').style.borderTop = '';
            
                for (let idx = 1; idx < users[current_user].length; idx ++) {
                    document.querySelector('.col-1').innerHTML += `<div class="msg-row msg-row${users[current_user][idx][0] == username ? '2' : ''}">
                                                                    <div class="msg-text">
                                                                        <h2>${users[current_user][idx][0]}</h2>
                                                                        <p>${users[current_user][idx][1]}</p>
                                                                    </div>
                                                                </div>`
                }
            }

            let messages = document.querySelector('.col-1').querySelectorAll('.msg-text')
            for ( let idx = 1; idx < messages.length; idx ++) {
                messages[idx].scrollIntoView()
            }

            document.querySelector('.msg-input img').onclick = ( event ) => {
                const el = document.querySelector('.msg-input .game-starter')
                el.classList.toggle('hidden')
            }

            const tournament_rounds = document.getElementById('tournaments')
            tournament_rounds.innerHTML = ''
            let found = false;
            for (let tournament in rounds) {
                for (let iround in rounds[tournament]) {
                    let   round  = rounds[tournament][iround]
                    if (round.player2 == username
                     && round.player1 == current_user) {
                        found = true
                        tournament_rounds.innerHTML += `<p>${tournament} - ${round.format}</p>`
                    }
                }
            }

            document.getElementById('tournaments-name').innerHTML = found ? 'Tournois' : ''

            build_buttons()
        }
    }

})());

import {createStore} from 'vuex'

export default createStore({
    state: {
        Me: {},
        profile_image: '',
        display_name: '',
        roles: []
    },
    getters: {},
    mutations: {
        UpdateMe(state, Me) {
            debugger
            state.Me = Me.me
            state.profile_image = Me.me.profile_image_url
            state.display_name = Me.me.display_name
            state.roles = Me.roles


        }

    },
    actions: {},
    modules: {}
})


const appStore = {
    state: {
        Roles: '',
        networkState: true
    },
    mutations: {
        updateRoles(state: any, value: string) {
            state.Roles = value
        },
        updateNetworkState(state: any, value: boolean) {
            state.networkState = value
        }
    },
    actions: {
        setNetworkState(context: any, value: boolean) {
            context.commit('updateNetworkState', value)
        },
        setRoles(context: any, value: string) {
            context.commit('updateRoles', value)
        },
        resetRoles(context: any) {
            context.commit('updateRoles', '')
        },
    }
}

export default appStore;

import {API} from "@/api";
import store from "@/store";

let Me: any = null;

export async function UpdateMe() {
    try {
        console.log("updating..")
        Me = await API.get_me()
        debugger
        store.commit('UpdateMe',Me)
        console.log(Me)
    } catch (e) {
        console.log('update failed ')
        console.log(e)
        Me = null
    } finally {

    }
    return Me
}

export function HasRole(role_name: string) {

    if (Me === null) {
        return false
    }

    for (const role of Me.roles) {
        if (role_name === role)
            return true
    }
    if (role_name.trim().length === 0)
        return true // no role checks login

    return false
}

export function IsLoggedIn() {
    return Me !== null

}

export function DisplayName() {

    if (Me === null) return ""
    return Me.me.display_name
}

export function ProfileImage() {
    if (Me === null) return ""
    return Me.me.profile_image_url
}

export function get_me() {
    return Me
}

UpdateMe()
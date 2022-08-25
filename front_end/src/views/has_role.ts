import {API} from "@/api";

let Me: any = null;

export async function UpdateMe() {
    try {
        console.log("updating..")
        Me = await API.get_me()
        console.log(Me)
    } catch (e) {
        console.log('update failed ')
        console.log(e)
        Me = null
    } finally {

    }
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
    return Me.display_name
}

export function ProfileImage() {

    return Me.profile_image_url
}

export function get_me() {
    return Me
}


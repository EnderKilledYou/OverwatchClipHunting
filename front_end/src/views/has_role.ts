import {API} from "@/api";

let Me: any = null;

export async function UpdateMe() {
    try {
        Me = await API.get_me()
    } catch (e) {
        Me = null
    } finally {

    }
}

export function HasRole(role_name: string) {

    if (Me === null) {
        return false
    }
    debugger
    for (const role of Me.roles) {
        if (role_name === role)
            return true
    }

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
    if (Me === null) return ""
    return Me.profile_image_url
}

export function get_me() {
    return Me
}

UpdateMe()
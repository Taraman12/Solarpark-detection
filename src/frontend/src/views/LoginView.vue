<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useApiFetch } from '@/plugins/fetch';
import { saveLocalToken, getLocalToken } from "@/stores/login.js";
// import FormField from '@/components/FormField.vue'
// import { computed, ref } from "vue";

const BASE_IP = import.meta.env.VITE_BASE_IP || 'localhost';
const baseURL = `http://${BASE_IP}:8000/api/v1`;

const { get, post, logInGetToken, getMe } = useApiFetch()
// async function post(url, data) {
//     const response = await fetch(`${baseURL}${url}`, {
//         method: 'POST',
//         headers: {
//             "Content-Type": "application/x-www-form-urlencoded",
//         },
//         body: data,
//     })
//     return response;
// }

const email = ref("");
const hidePassword = ref(true);
const password = ref("");

const passwordFieldIcon = computed(() => hidePassword.value ? "fa-eye" : "fa-eye-slash");
const passwordFieldType = computed(() => hidePassword.value ? "password" : "text");

// const doLogin = () => alert("Not implemented yet :O");
async function doLogin() {
    try {
        console.log(email.value);
        const response = await logInGetToken(email.value, password.value);
        const data = await response;
        console.log(data.access_token);
        saveLocalToken(data.access_token);
        return data;
    } catch (error) {
        console.error(error);
    }
}

async function checkLogin() {
    try {
        const token = getLocalToken();
        console.log(token);
        const response = await getMe(token);
        return response;
    }
    catch (error) {
        console.error(error);
    }
}
</script>


<template>
    <div class="grid gap-4 justify-center mt-4">
        <div id="login">
            <div id="description">
                <h1>Login</h1>
            </div>
            <div id="form">
                <form @submit.prevent="doLogin">
                    <label for="email">Email</label>
                    <input type="text" id="email" v-model="email" placeholder="elon@musk.io" autocomplete="off">

                    <label for="password">Password</label>&nbsp;
                    <i class="fas" :class="[passwordFieldIcon]" @click="hidePassword = !hidePassword"></i>
                    <input :type="passwordFieldType" id="password" v-model="password" placeholder="**********">

                    <button type="submit">Log in</button>
                </form>
            </div>
        </div>
        <div>
            <button @click="checkLogin()">Check</button>
        </div>
    </div>
</template>

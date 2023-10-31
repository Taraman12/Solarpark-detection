/* eslint-disable no-undef */
import { ref } from 'vue'

const BASE_IP = import.meta.env.VITE_BASE_IP || 'localhost';

// function authHeaders(token) {
//     return {
//         headers: {
//             Authorization: `Bearer ${token}`,
//         },
//     };
// }

function createFetch(baseURL) {
    return function useFetch() {

        const data = ref(null)
        const error = ref(null)
        const headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            // "Access-Control-Allow-Private-Network": "true",
        };
        async function get(url) {
            const response = await fetch(`${baseURL}${url}`, {
                method: 'GET',
                headers: headers
            })
            return response;
        }

        async function post(url, data) {
            const response = await fetch(`${baseURL}${url}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(data),
            })
            return response;
        }

        async function filePost(url, data) {
            const response = await fetch(`${baseURL}${url}`, {
                method: 'POST',
                headers: headers,
                body: data,
            })
            return response;
        }

        async function put(url, data) {
            try {
                const response = await fetch(`${baseURL}${url}`, {
                    method: "PUT", // or 'PUT'
                    // mode: "cors",
                    headers: headers,
                    body: JSON.stringify(data),
                    formData: data,
                });

                const result = await response;
                return result;
            } catch (error) {
                console.error("Error:", error);
            }
        }
        async function logInGetToken(username, password) {
            const params = new URLSearchParams();
            params.append('username', username);
            params.append('password', password);
            const response = await fetch(`${baseURL}/login/access-token`, {
                method: 'POST',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: params,
            });
            const data = await response.json();
            return data;
        }
        async function getMe(token) {
            const response = await fetch(`${baseURL}/user/me`, {
                method: 'GET',
                headers: {
                    "Authorization": `Bearer ${token}`,
                }
            })
            return response;
        }
        // async function put(url, data) {
        //     console.log(JSON.stringify(data));
        //     const response = await fetch(`${baseURL}${url}`, {
        //         method: 'PUT',
        //         headers: headers,
        //         body: JSON.stringify(data),
        //     })
        //     console.log(response);
        //     return response.json();
        // }
        // function put(url, body, headers={}) {
        //     return fetch(`${baseURL}${url}`, {
        //         method: 'PUT',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             ...headers
        //         },
        //         body: JSON.stringify(body)
        //     })
        //         .then((res) => res.json())
        //         .then((json) => (data.value = json))
        //         .catch((err) => (error.value = err))
        // }

        function del(url) {
            return fetch(`${baseURL}${url}`, {
                method: 'DELETE',
                headers
            })
                .then((res) => res.json())
                .then((json) => (data.value = json))
                .catch((err) => (error.value = err))
        }

        return { data, error, get, post, filePost, put, del, logInGetToken, getMe }
    }
}
// const DOCKERIZED = process.env.DOCKERIZED || false;
// const API_URL = DOCKERIZED ? 'api' : 'localhost';
export const useApiFetch = createFetch(`http://${BASE_IP}:8000/api/v1`)

/* eslint-disable no-undef */
import { ref } from 'vue'
import { useToast } from "vue-toastification";
import { useMainStore } from '@/stores/main'
// import { VITE_BASE_IP } from '@/config'

const mainStore = useMainStore()


// const BASE_IP = import.meta.env.VITE_BASE_IP || 'localhost';
const BASE_IP = 'localhost'

const toast = useToast()

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
      'Authorization': `Bearer ${mainStore.access_token}`,
      // "Access-Control-Allow-Private-Network": "true",
    };
    async function get(endpoint, params) {
      let url = new URL(`${baseURL}${endpoint}`);
      if (params) {
        url.search = new URLSearchParams(params).toString();
      }
      const response = await fetch(url, {
        method: 'GET',
        headers: headers
      })
      const data = await response.json();
      return data;
    }

    async function post(endpoint, params, payload) {
      let url = new URL(`${baseURL}${endpoint}`);
      if (params) {
        url.search = new URLSearchParams(params).toString();
      }
      const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(payload),
      })
      if (response.status === 401 || response.status === 403) {
        toast.error('Not logged in', { timeout: 1500 });
        return null;
      }
      return response;
    }

    async function filePost(url, payload) {
      const response = await fetch(`${baseURL}${url}`, {
        method: 'POST',
        headers: headers,
        body: payload,
      })
      return response;
    }

    async function put(url, payload) {
      try {
        const response = await fetch(`${baseURL}${url}`, {
          method: "PUT", // or 'PUT'
          // mode: "cors",
          headers: headers,
          body: JSON.stringify(payload),
          formData: payload,
        });

        const result = await response;
        return result;
      } catch (error) {
        console.error("Error:", error);
      }
    }

    async function logInGetToken(username, password) {
      // should be named params, because it is a payload
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      try {
        const response = await fetch(`${baseURL}login/access-token`, {
          method: 'POST',
          headers: {
            'Access-Control-Allow-Origin': '*',
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: params,
        });

        if (!response.ok) {
          const data = await response.json();
          throw new Error(data.errors[0] || 'Network response was not ok');
        }

        const data = await response.json();
        return data;
      } catch (err) {
        error.value = err.message;
        toast.error(err.message);
        return null;
      }
    };



    //   const response = await fetch(`${baseURL}/login/access-token`, {
    //     method: 'POST',
    //     headers: {
    //       'Access-Control-Allow-Origin': '*',
    //       "Content-Type": "application/x-www-form-urlencoded",
    //     },
    //     body: params,
    //   });
    //   const data = await response.json();
    //   return data;
    // }
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
export const useFetch = createFetch(`http://${BASE_IP}:8000/api/v1/`)

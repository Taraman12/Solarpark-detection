import { ref } from 'vue'

function createFetch(baseURL) {
    return function useFetch() {
        const data = ref(null)
        const error = ref(null)

        function get(url) {
            return fetch(`${baseURL}${url}`, {
                method: 'GET'
            })
                .then((res) => res.json())
                .then((json) => (data.value = json))
                .catch((err) => (error.value = err))
        }

        function post(url, body, headers = {}) {
            return fetch(`${baseURL}${url}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(body)
            })
                .then((res) => res.json())
                .then((json) => (data.value = json))
                .catch((err) => (error.value = err))
        }

        function put(url, body, headers = {}) {
            return fetch(`${baseURL}${url}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    ...headers
                },
                body: JSON.stringify(body)
            })
                .then((res) => res.json())
                .then((json) => (data.value = json))
                .catch((err) => (error.value = err))
        }

        function del(url, headers = {}) {
            return fetch(`${baseURL}${url}`, {
                method: 'DELETE',
                headers
            })
                .then((res) => res.json())
                .then((json) => (data.value = json))
                .catch((err) => (error.value = err))
        }

        return { data, error, get, post, put, del }
    }
}

export const useApiFetch = createFetch('http://localhost:8000/api/v1')
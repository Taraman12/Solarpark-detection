// https://betterprogramming.pub/how-to-use-axios-in-an-optimized-and-scalable-way-with-react-c56fa632e088

import axios from 'axios'
import { useToast } from 'vue-toastification'

const BASE_IP = import.meta.env.VITE_BASE_IP || 'localhost';
// const BASE_IP = 'localhost'

const toast = useToast()

const axiosClient = axios.create();
axiosClient.defaults.baseURL = `http://${BASE_IP}:8000/api/v1/`;

// const axiosClient = axios.create({
//   baseURL: `http://${baseURL}:8000/api/v1/`,
//   timeout: 10000,
//   withCredentials: false,
//   headers: {
//     'Content-Type': 'application/json',
//     Accept: 'application/json'
//   }
// })

axiosClient.defaults.headers = {
  'Content-Type': 'application/json',
  Accept: 'application/json'
};

//All request will wait 2 seconds before timeout
axiosClient.defaults.timeout = 2000;

axiosClient.defaults.withCredentials = true;

export function getRequest(URL) {
  return axiosClient.get(`/${URL}`).then(response => response);
}

export function postRequest(URL, payload) {
  return axiosClient.post(`/${URL}`, payload).then(response => response);
}

export function patchRequest(URL, payload) {
  return axiosClient.patch(`/${URL}`, payload).then(response => response);
}

export function deleteRequest(URL) {
  return axiosClient.delete(`/${URL}`).then(response => response);
}

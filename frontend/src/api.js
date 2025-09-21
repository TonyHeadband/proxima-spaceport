import axios from 'axios';
import {INDEXER_API_BASE} from './config/routes.js';

const url = new URL(INDEXER_API_BASE,"http://localhost:8080").toString()

// Create an instance of axios with the base URL
const api = axios.create({
    baseURL: url,
});

// Export the Axios instance
export default api;
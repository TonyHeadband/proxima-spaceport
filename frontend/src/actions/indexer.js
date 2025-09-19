import api from '../api.js'
import { INDEXER_ROUTES } from '../config/routes.js'

// fetchRepositories accepts an optional AbortSignal via options and returns the data
export const fetchRepositories = async (options = {}) => {
    const { signal } = options
    try {
        const response = await api.get(INDEXER_ROUTES.repos.url, { signal })
        // return the raw data (array) to the caller
        return response.data
    } catch (error) {
        // surface network/errors to caller
        console.error('Error fetching repositories:', error)
        throw error
    }
}

// fetchRepositories accepts an optional AbortSignal via options and returns the data
export const addNewRepository = async (repositoryData, options = {}) => {
    const { signal } = options
    try {
        console.log('Adding new repository via API…', repositoryData)
        const response = await api.post(INDEXER_ROUTES.repos.url, repositoryData, { signal })
        // return the raw data (array) to the caller
        return response.data
    } catch (error) {
        // surface network/errors to caller
        console.error('Error adding new repository:', error)
        throw error
    }
}

const indexer = { fetchRepositories, addNewRepository }
export default indexer

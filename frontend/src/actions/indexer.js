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

// EditRepository accepts an optional AbortSignal via options and returns the data
export const EditRepository = async (id, repositoryData, options = {}) => {
    const { signal } = options
    try {
        console.log(`Editing repository ${id} via API…`, repositoryData)
        const response = await api.put(`${INDEXER_ROUTES.repos.url}/${id}`, repositoryData, { signal })
        // return the raw data (array) to the caller
        return response.data
    } catch (error) {
        // surface network/errors to caller
        console.error('Error editing repository:', error)
        throw error
    }
}

// DeleteRepository accepts an optional AbortSignal via options and returns the data
export const DeleteRepository = async (id, options = {}) => {
    const { signal } = options  
    try {
        console.log(`Deleting repository ${id} via API…`)
        const response = await api.delete(`${INDEXER_ROUTES.repos.url}/${id}`, { signal })
        // return the raw data (array) to the caller
        return response.data
    } catch (error) {
        // surface network/errors to caller
        console.error('Error deleting repository:', error)
        throw error
    }
}

const indexer = { fetchRepositories, addNewRepository, EditRepository, DeleteRepository }
export default indexer

import React from 'react'
import Button from './Button.jsx'
import { validateNewRepo } from '../helpers/validators'
import indexer from '../actions/indexer.js'
import styles from './ReposContentSection.module.css'
import HomeStyles from '../pages/home.module.css'

function formatDate(iso) {
    if (!iso) return ''
    try {
        const d = new Date(iso)
        return d.toLocaleString('en-US', { timeZone: 'America/Toronto', timeZoneName: 'short' })
    } catch (e) {
        return iso
    }
}

export default function ReposContentSection() {
    const [repos, setRepos] = React.useState([])
    const [loading, setLoading] = React.useState(true)
    const [error, setError] = React.useState(null)
    const [showNewRow, setShowNewRow] = React.useState(false)
    const [showActions, setShowActions] = React.useState(false)
    const [editingId, setEditingId] = React.useState(null)

    React.useEffect(() => {
        let mounted = true
        const controller = new AbortController()

        const load = async () => {
            console.log('Loading repositories from API…')
            setLoading(true)
            setError(null)
            try {
                const data = await indexer.fetchRepositories({ signal: controller.signal })
                if (!mounted) return
                setRepos(Array.isArray(data) && data.length ? data : [])
            } catch (err) {
                console.error('Failed to load repos, using sample data', err)
                if (!mounted) return
                setError(err)
            } finally {
                if (!mounted) return
                setLoading(false)
            }
        }

        load()

        return () => {
            mounted = false
            controller.abort()
        }
    }, [])

    function toggleShowActions() {
        setShowActions((s) => !s)
    }

    return (
        <section className={styles.contentPanel}>
            <h2 className={HomeStyles.contentTitle}>Repositories</h2>

            <div className={styles.tableWrap}>
                {loading && <div style={{ padding: 12 }}>Loading repositories…</div>}
                {error && <div style={{ padding: 12, color: '#fca5a5' }}>Failed to load repositories — showing sample data.</div>}
                {(repos.length === 0) && <div style={{ padding: 12, color: '#ffc825ff' }}>No repositories found.</div>}
                <table className={styles.repoTable}>
                    <thead>
                        <tr>
                            <th className={styles.nameCell}>Name</th>
                            <th className={styles.urlCell}>URL</th>
                            <th className={styles.branchCell}>Branch</th>
                            <th className={styles.composeCell}>Compose Folder</th>
                            <th className={styles.credentialsCell}>Credentials</th>
                            {!showActions && <th className={styles.indexedAtCell}>Indexed at</th>}
                            {!showActions && <th className={styles.updatedAtCell}>Updated at</th>}
                            {showActions && <th className={styles.actionsCell}>Actions</th>}
                        </tr>
                    </thead>
                    <tbody>
                        {repos.map((r) => (
                            <RowComponent
                                key={r.id}
                                repo={r}
                                editingId={editingId}
                                setEditingId={setEditingId}
                                setRepos={setRepos}
                                showActions={showActions}
                            />
                        ))}
                        {showNewRow && (
                            <NewRowComponent showActions={showActions} setShowNewRow={setShowNewRow} setRepos={setRepos} />
                        )}
                    </tbody>
                </table>
            </div>

            <div className={styles.actionArea}>
                {(showActions && !showNewRow && !editingId) && (
                    <Button
                        label={'Add Repository'}
                        className={`${styles.actionButton} ${styles.actionButtonVar01}`}
                        type="button"
                        onClick={() => setShowNewRow(true)}
                    />
                )}
                <Button
                    label={showActions ? 'Hide modifying tools' : 'Modify Table'}
                    className={styles.actionButton}
                    type="button"
                    onClick={toggleShowActions}
                />
            </div>
        </section>
    )
}

function RowComponent({ repo, editingId, setEditingId, setRepos, showActions }) {
    const isEditing = editingId === repo.id

    const [form, setForm] = React.useState({
        name: repo.name || '',
        url: repo.url || '',
        branch: repo.branch || 'main',
        compose_folder: repo.compose_folder || '',
        credentials_name: repo.credentials_name || '',
    })
    const [submitting, setSubmitting] = React.useState(false)

    React.useEffect(() => {
        // sync form when editing begins or repo changes
        setForm({
            name: repo.name || '',
            url: repo.url || '',
            branch: repo.branch || 'main',
            compose_folder: repo.compose_folder || '',
            credentials_name: repo.credentials_name || '',
        })
    }, [isEditing, repo])

    const onChange = (e) => {
        const { name, value } = e.target
        setForm((s) => ({ ...s, [name]: value }))
    }

    const onStartEdit = () => setEditingId(repo.id)

    const onDelete = async () => {
        if (!window.confirm(`Are you sure you want to delete the repository "${repo.name}"? This action cannot be undone.`)) return
        try {
            await indexer.DeleteRepository(repo.id)
            setRepos((prev) => prev.filter((p) => p.id !== repo.id))
        } catch (err) {
            console.error('Error deleting repository:', err)
        }
    }

    const onConfirm = async () => {
        setSubmitting(true)
        try {
            const payload = { ...form }
            const updated = await indexer.EditRepository(repo.id, payload)
            // Prefer server-returned object to populate authoritative fields.
            console.log('Updated repo from server:', updated)
            if (updated) {
                setRepos((prev) => prev.map((p) => (p.id === repo.id ? { ...p, ...updated } : p)))
            }
            setEditingId(null)
        } catch (err) {
            console.error('Failed to update repo', err)
            alert('Failed to save changes — check console for details')
        } finally {
            setSubmitting(false)
        }
    }

    const onCancel = () => setEditingId(null)

    if (!isEditing) {
        return (
            <tr>
                <td className={styles.nameCell}>{repo.name}</td>
                <td className={styles.urlCell} title={repo.url}>{repo.url}</td>
                <td className={styles.branchCell}>{repo.branch}</td>
                <td className={styles.composeCell}>{repo.compose_folder || '—'}</td>
                <td className={styles.credentialsCell}>{repo.credentials_name || '—'}</td>
                {!showActions && <td>{formatDate(repo.indexed_at) || '—'}</td>}
                {!showActions && <td>{formatDate(repo.updated_at) || '—'}</td>}
                {showActions && <td className={styles.actionsCell}>
                    <div className={styles.rowActions}>
                        <Button label="Edit" className={`${styles.smallButton}`} type="button" onClick={onStartEdit} />
                        <Button label="Delete" className={`${styles.smallButton} ${styles.warningButton}`} type="button" onClick={onDelete} />
                    </div>
                </td>}
            </tr>
        )
    }

    return (
        <tr className={styles.newRow} key={`edit-${repo.id}`}>
            <td>
                <input name="name" value={form.name} onChange={onChange} className={styles.inlineInput} />
            </td>
            <td>
                <input name="url" value={form.url} onChange={onChange} className={styles.inlineInput} />
            </td>
            <td>
                <input name="branch" value={form.branch} onChange={onChange} className={styles.inlineInput} />
            </td>
            <td>
                <input name="compose_folder" value={form.compose_folder} onChange={onChange} className={styles.inlineInput} />
            </td>
            <td>
                <input name="credentials_name" value={form.credentials_name} onChange={onChange} className={styles.inlineInput} />
            </td>
            {!showActions && <td>—</td>}
            {!showActions && <td>—</td>}
            <td className={styles.actionsCell}>
                <div className={styles.newRowActions}>
                    <Button label={submitting ? 'Saving…' : 'Confirm'} className={styles.smallButton} onClick={onConfirm} disabled={submitting} />
                    <Button label="Cancel" className={styles.smallButton01} onClick={onCancel} />
                </div>
            </td>
        </tr>
    )
}

function NewRowComponent({ showActions, setShowNewRow, setRepos }) {
    const [form, setForm] = React.useState({
        name: '',
        url: '',
        branch: 'main',
        compose_folder: '',
        credentials_name: '',
    })
    const [fieldErrors, setFieldErrors] = React.useState({})
    const [submitting, setSubmitting] = React.useState(false)

    const onChange = (e) => {
        const { name, value } = e.target
        setForm((s) => ({ ...s, [name]: value }))
        setFieldErrors((fe) => ({ ...fe, [name]: undefined }))
    }

    const onSave = async () => {
        const res = validateNewRepo({ name: form.name, url: form.url, branch: form.branch })
        if (!res.ok) {
            const fe = {}
            res.errors.forEach((msg) => {
                const lower = msg.toLowerCase()
                if (lower.includes('name')) fe.name = msg
                else if (lower.includes('url')) fe.url = msg
                else if (lower.includes('branch')) fe.branch = msg
            })
            setFieldErrors(fe)
            return
        }

        setSubmitting(true)
        try {
            const payload = { ...form }
            const created = await indexer.addNewRepository(payload)
            const toInsert = created && created.id ? created : {
                id: `r${Date.now()}`,
                updated_at: new Date().toISOString(),
                indexed_at: null,
                ...payload,
            }
            setRepos((prev) => [toInsert, ...prev])
            setShowNewRow(false)
            setForm({ name: '', url: '', branch: 'main', compose_folder: '', credentials_name: '' })
            setFieldErrors({})
        } catch (err) {
            console.error('Failed to save new repo', err)
            alert('Failed to save repository — check console for details')
        } finally {
            setSubmitting(false)
        }
    }

    return (
        <tr className={styles.newRow}>
            <td>
                <input
                    name="name"
                    value={form.name}
                    onChange={onChange}
                    className={styles.inlineInput}
                    placeholder="name/repo"
                />
                {fieldErrors.name && <div className={styles.fieldError}>{fieldErrors.name}</div>}
            </td>
            <td>
                <input
                    name="url"
                    value={form.url}
                    onChange={onChange}
                    className={styles.inlineInput}
                    placeholder="git url"
                />
                {fieldErrors.url && <div className={styles.fieldError}>{fieldErrors.url}</div>}
            </td>
            <td>
                <input
                    name="branch"
                    value={form.branch}
                    onChange={onChange}
                    className={styles.inlineInput}
                    placeholder="branch"
                />
                {fieldErrors.branch && <div className={styles.fieldError}>{fieldErrors.branch}</div>}
            </td>
            <td>
                <input
                    name="compose_folder"
                    value={form.compose_folder}
                    onChange={onChange}
                    className={styles.inlineInput}
                    placeholder="compose folder"
                />
            </td>
            {!showActions && <td>—</td>}
            {!showActions && <td>—</td>}
            <td>
                <input
                    name="credentials_name"
                    value={form.credentials_name}
                    onChange={onChange}
                    className={styles.inlineInput}
                    placeholder="credentials name"
                />
            </td>
            <td className={styles.actionsCell}>
                <div className={styles.newRowActions}>
                    <Button label={submitting ? 'Saving…' : 'Save'} className={styles.smallButton} onClick={onSave} disabled={submitting} />
                    <Button label="Cancel" className={styles.smallButton01} onClick={() => {
                        setShowNewRow(false)
                        setForm({ name: '', url: '', branch: 'main', compose_folder: '', credentials_name: '' })
                        setFieldErrors({})
                    }} />
                </div>
            </td>
        </tr>
    )
}

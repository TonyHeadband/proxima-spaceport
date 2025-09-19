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
        return d.toLocaleString()
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
                            <tr key={r.id}>
                                <td className={styles.nameCell}>{r.name}</td>
                                <td className={styles.urlCell} title={r.url}>{r.url}</td>
                                <td className={styles.branchCell}>{r.branch}</td>
                                <td className={styles.composeCell}>{r.compose_folder || '—'}</td>
                                <td className={styles.credentialsCell}>{r.credentials_name || '—'}</td>
                                {!showActions && <td>{formatDate(r.indexed_at) || '—'}</td>}
                                {!showActions && <td>{formatDate(r.updated_at) || '—'}</td>}
                                {showActions && <td className={styles.actionsCell}>
                                    <div className={styles.rowActions}>
                                        <EditRowComponent showActions={showActions} repo={r} />
                                    </div>
                                </td>}
                            </tr>
                        ))}
                        {showNewRow && (
                            <NewRowComponent showActions={showActions} setShowNewRow={setShowNewRow} setRepos={setRepos} />
                        )}
                    </tbody>
                </table>
            </div>

            <div className={styles.actionArea}>
                {(showActions && !showNewRow) && (
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

function EditRowComponent({ showActions, repo }) {
    if (!showActions) return '—'

    return (
        <>
            <Button
                label="Edit"
                type="button"
                className={styles.smallButton}
                onClick={() => console.log('edit', repo.id)}
            />
            <Button
                label="Delete"
                className={`${styles.smallButton} ${styles.warningButton}`}
                type="button"
                onClick={() => console.log('delete', repo.id)}
            />
        </>
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

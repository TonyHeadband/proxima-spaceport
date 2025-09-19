import React from 'react'
import Button from './Button.jsx'
import { validateNewRepo } from '../helpers/validators'
import styles from './ContentPanel.module.css'
import HomeStyles from '../pages/home.module.css'

function ContentPanel({ active }) {
    if (active === 'repos') {
        return <ReposContentSection />
    }

    return (
        <section className={styles.contentPanel}>
            <h2 className={HomeStyles.contentTitle}>{active}</h2>
            <p>Content for <strong>{active}</strong> goes here.</p>
        </section>
    )
}

function formatDate(iso) {
    if (!iso) return ''
    try {
        const d = new Date(iso)
        return d.toLocaleString()
    } catch (e) {
        return iso
    }
}

function ReposContentSection() {
    // static example data matching RepositoryModel in backend/app/models/indexer.py
    const sampleInitial = [
        {
            id: 'r1',
            url: 'https://github.com/example/repo-frontend.git',
            branch: 'main',
            name: 'example/repo-frontend',
            compose_folder: 'docker',
            indexed_at: '2025-09-10T12:34:56Z',
            updated_at: '2025-09-12T15:00:00Z',
            credentials_name: 'github-token-1',
        },
        {
            id: 'r2',
            url: 'https://git.example.com/other/repo-backend.git',
            branch: 'develop',
            name: 'other/repo-backend',
            compose_folder: null,
            indexed_at: null,
            updated_at: '2025-08-01T09:20:00Z',
            credentials_name: null,
        },
    ]

    const [repos, setRepos] = React.useState(sampleInitial)
    const [showNewRow, setShowNewRow] = React.useState(false)
    const [showActions, setShowActions] = React.useState(false)

    function toggleShowActions() {
        setShowActions((s) => !s)
    }

    return (
        <section className={styles.contentPanel}>
            <h2 className={HomeStyles.contentTitle}>Repositories</h2>

            <div className={styles.tableWrap}>
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
    return (
        <tr className={styles.newRow}>
            <td><input className={styles.inlineInput} placeholder="name/repo" id="new-name" /></td>
            <td><input className={styles.inlineInput} placeholder="git url" id="new-url" /></td>
            <td><input className={styles.inlineInput} placeholder="branch" id="new-branch" defaultValue="main" /></td>
            <td><input className={styles.inlineInput} placeholder="compose folder" id="new-compose" /></td>
            {!showActions && <td>—</td>}
            {!showActions && <td>—</td>}
            <td><input className={styles.inlineInput} placeholder="credentials name" id="new-cred" /></td>
            <td className={styles.actionsCell}>
                <div className={styles.newRowActions}>
                    <Button label="Save" className={styles.smallButton} onClick={() => {
                        const name = document.getElementById('new-name').value
                        const url = document.getElementById('new-url').value
                        const branch = document.getElementById('new-branch').value
                        // Validate user entries
                        const res = validateNewRepo({ name, url, branch })
                        if (!res.ok) {
                            // simple error feedback for now
                            alert('Invalid input:\n' + res.errors.join('\n'))
                            return
                        }

                        const newRepo = {
                            id: `r${Date.now()}`,
                            name,
                            url,
                            branch,
                            compose_folder: document.getElementById('new-compose').value || null,
                            indexed_at: null,
                            updated_at: new Date().toISOString(),
                            credentials_name: document.getElementById('new-cred').value || null,
                        }
                        setRepos((prev) => [newRepo, ...prev])
                        setShowNewRow(false)
                    }} />
                    <Button label="Cancel" className={styles.smallButton01} onClick={() => setShowNewRow(false)} />
                </div>
            </td>
        </tr>
    )
}
export default ContentPanel

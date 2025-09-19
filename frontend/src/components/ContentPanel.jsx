import React from 'react'
import styles from './ContentPanel.module.css'
import HomeStyles from '../pages/home.module.css'
import ReposContentSection from './ReposContentSection.jsx'

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

// ReposContentSection and helpers moved to their own file
export default ContentPanel

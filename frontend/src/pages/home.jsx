import { useState } from 'react'
import Header from '../components/header'
import Menu from '../components/menu'
import ContentPanel from '../components/ContentPanel'

import styles from './home.module.css'

function Home() {
    const [active, setActive] = useState('item-1')

    return (
        <>
            <Header />
            <div className={styles['layout-row']}>
                <nav className={styles['left-col']}>
                    <Menu activeItem={active} onSelect={setActive} />
                </nav>

                <main className={styles['right-col']}>
                    <ContentPanel active={active} />
                </main>
            </div>
        </>
    )
}

export default Home

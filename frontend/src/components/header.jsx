import styles from './header.module.css'

function Header() {
  return (
    <header className={`${styles.headerBox}`}>
      {<p className={`${styles.headerText}`}>Spaceport</p>}
    </header>
  )
}

export default Header
import styles from './Button.module.css'

function Button({ label, isActive, onClick, disabled = false, className = '', type = 'button', ...rest }) {
    const classes = [styles.menuButton, isActive ? styles.active : null, className].filter(Boolean).join(' ')

    return (
        <button
            type={type}
            className={classes}
            aria-current={isActive ? 'true' : undefined}
            onClick={(e) => onClick && onClick(e)}
            disabled={disabled}
            {...rest}
        >
            {label}
        </button>
    )
}

export default Button
import styles from './menu.module.css'
import Button from './Button.jsx'
import DEFAULT_MENU_ITEMS from '../config/menu.js'

// Menu expects an array of item objects. Item shape:
// { id: string, label: string, href?, icon?, badge?, disabled?, onClick?(item) }
// onSelect will be called with the selected item's id (string).
function Menu({ items = DEFAULT_MENU_ITEMS, activeItem = null, onSelect = () => { } }) {
    return (
        <nav className={styles.menu} aria-label="Main navigation">
            {items.map((item) => {
                const isActive = item.id === activeItem
                return (
                    <Button
                        key={item.id}
                        label={item.label}
                        isActive={isActive}
                        disabled={item.disabled}
                        onClick={(e) => {
                            // allow item-specific handler first
                            if (item.onClick) item.onClick(item)
                            // then notify parent with stable id
                            onSelect(item.id)
                        }}
                    />
                )
            })}
        </nav>
    )
}

export default Menu
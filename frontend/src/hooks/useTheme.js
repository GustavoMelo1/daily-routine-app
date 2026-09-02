import { useLayoutEffect, useState } from "react"

const STORAGE_KEY = "daily-routine-theme"

function getInitialTheme() {
  const savedTheme = window.localStorage.getItem(STORAGE_KEY)
  if (savedTheme === "light" || savedTheme === "dark") return savedTheme

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export default function useTheme() {
  const [theme, setTheme] = useState(getInitialTheme)

  useLayoutEffect(() => {
    const dark = theme === "dark"
    document.documentElement.classList.toggle("dark", dark)
    document.documentElement.style.colorScheme = theme
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  function toggleTheme() {
    setTheme((current) => (current === "dark" ? "light" : "dark"))
  }

  return { theme, toggleTheme }
}

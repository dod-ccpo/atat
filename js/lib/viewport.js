export const isNotInVerticalViewport = (el) => {
  const bounds = el.getBoundingClientRect()

  if (bounds.top < 0) {
    return true
  }

  if (bounds.bottom > window.innerHeight - 50) {
    // 50 is a magic number to offset for the sticky footer
    // see variables.scss for $footer-height
    return true
  }

  return false
}

// https://stackoverflow.com/a/6020820

// List of HTML entities for escaping.
const htmlEscapes = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
}

const htmlEscaper = /[&<>"'\/]/g

// Escape a string for HTML interpolation.
const escape = (string) => {
  return ('' + string).replace(htmlEscaper, (match) => htmlEscapes[match])
}

export default escape

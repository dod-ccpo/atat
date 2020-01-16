import createNumberMask from 'text-mask-addons/dist/createNumberMask'
import emailMask from 'text-mask-addons/dist/emailMask'
import createAutoCorrectedDatePipe from 'text-mask-addons/dist/createAutoCorrectedDatePipe'

export default {
  anything: {
    mask: false,
    match: /\s*/,
    unmask: [],
    validationError: 'Please enter a response',
  },
  date: {
    mask: [/\d/, /\d/, '/', /\d/, /\d/, '/', /\d/, /\d/, /\d/, /\d/],
    match: /(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d/,
    unmask: [],
    pipe: createAutoCorrectedDatePipe('mm/dd/yyyy HH:MM'),
    keepCharPositions: true,
    validationError: 'Please enter a valid date in the form MM/DD/YYYY',
  },
  dodId: {
    mask: createNumberMask({
      prefix: '',
      allowDecimal: false,
      allowLeadingZeroes: true,
      includeThousandsSeparator: false,
    }),
    match: /^\d{10}$/,
    unmask: [],
    validationError: 'Please enter a 10-digit DoD ID number',
  },
  dollars: {
    mask: createNumberMask({ prefix: '$', allowDecimal: true }),
    match: /^-?\d+\.?\d*$/,
    unmask: ['$', ','],
    validationError: 'Please enter a dollar amount',
  },
  clinDollars: {
    mask: createNumberMask({ prefix: '$', allowDecimal: true }),
    match: /^-?\d+\.?\d*$/,
    unmask: ['$', ','],
    validationError:
      'Please enter a dollar amount between $0.00 and $1,000,000,000.00',
  },
  email: {
    mask: emailMask,
    match: /^.+@[^.].*\.[a-zA-Z]{2,10}$/,
    unmask: [],
    validationError: 'Please enter a valid e-mail address',
  },
  integer: {
    mask: createNumberMask({ prefix: '', allowDecimal: false }),
    match: /^[1-9]\d*$/,
    unmask: [','],
    validationError: 'Please enter a number',
  },
  phoneExt: {
    mask: createNumberMask({
      prefix: '',
      allowDecimal: false,
      integerLimit: 10,
      allowLeadingZeroes: true,
      includeThousandsSeparator: false,
    }),
    match: /^\d{0,10}$/,
    unmask: [],
    validationError: 'Optional: Please enter up to 10 digits',
  },
  portfolioName: {
    mask: false,
    match: /^.{4,100}$/,
    unmask: [],
    validationError: 'Portfolio names can be between 4-100 characters',
  },
  requiredField: {
    mask: false,
    match: /.+/,
    unmask: [],
    validationError: 'This field is required',
  },
  taskOrderNumber: {
    mask: false,
    match: /^.{13}$/,
    unmask: [],
    validationError: 'TO number must be 13 digits',
  },
  usPhone: {
    mask: [
      '(',
      /[1-9]/,
      /\d/,
      /\d/,
      ')',
      ' ',
      /\d/,
      /\d/,
      /\d/,
      '-',
      /\d/,
      /\d/,
      /\d/,
      /\d/,
    ],
    match: /^\d{10}$/,
    unmask: ['(', ')', '-', ' '],
    validationError: 'Please enter a 10-digit phone number',
  },
  restrictedFileName: {
    mask: false,
    match: /^[A-Za-z0-9\-_ \.]+$/,
    unmask: [],
    validationError:
      'File names can only contain the characters A-Z, 0-9, space, hyphen, underscore, and period.',
  },
}

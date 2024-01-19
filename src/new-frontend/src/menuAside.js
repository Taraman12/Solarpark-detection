import {
  mdiAccountCircle,
  mdiMonitor,
  mdiViewListOutline,
  mdiLightbulbOn,
  mdiHome,
  mdiLock,
  mdiAlertCircle,
  mdiSquareEditOutline,
  mdiTable,
  mdiViewList,
  mdiTelevisionGuide,
  mdiResponsive,
  mdiPalette,
} from '@mdi/js'

export default [
  {
    to: '/',
    icon: mdiHome,
    label: 'Home'
  },
  {
    to: '/overview',
    icon: mdiViewListOutline,
    label: 'Overview'
  },
  {
    to: '/classifying',
    icon: mdiViewListOutline,
    label: 'Classifying'
  },
  {
    to: '/model',
    icon: mdiLightbulbOn,
    label: 'Model'
  },
  {
    to: '/dashboard',
    icon: mdiMonitor,
    label: 'Dashboard'
  },
  {
    to: '/tables',
    label: 'Tables',
    icon: mdiTable
  },
  {
    to: '/forms',
    label: 'Forms',
    icon: mdiSquareEditOutline
  },
  {
    to: '/ui',
    label: 'UI',
    icon: mdiTelevisionGuide
  },
  {
    to: '/responsive',
    label: 'Responsive',
    icon: mdiResponsive
  },
  {
    to: '/',
    label: 'Styles',
    icon: mdiPalette
  },
  {
    to: '/profile',
    label: 'Profile',
    icon: mdiAccountCircle
  },
  {
    to: '/login',
    label: 'Login',
    icon: mdiLock
  },
  {
    to: '/error',
    label: 'Error',
    icon: mdiAlertCircle
  },
  {
    label: 'Dropdown',
    icon: mdiViewList,
    menu: [
      {
        label: 'Item One'
      },
      {
        label: 'Item Two'
      }
    ]
  }
]

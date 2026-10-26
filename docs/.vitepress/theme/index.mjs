import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app, router, siteData }) {
    // Injeções futuras de componentes Vue globais de telemetria se necessário
  },
}

import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'Missão Aurora Siger',
    description: 'Documentação Técnica & Centro de Comando da Missão em Marte',
    base: process.env.GITHUB_ACTIONS ? '/PBL-Aurora/' : '/',
    head: [
      [
        'link',
        {
          rel: 'icon',
          href: 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚀</text></svg>',
        },
      ],
      ['meta', { name: 'theme-color', content: '#0B0E14' }],
      ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
      ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }],
    ],
    markdown: {
      lineNumbers: true,
    },
    mermaid: {
      theme: 'dark',
      darkTheme: true,
    },
    themeConfig: {
      logo: '🚀',
      siteTitle: 'AURORA SIGER // MARS CONTROL',
      nav: [
        { text: 'Visão Geral', link: '/' },
        { text: 'Arquitetura', link: '/architecture' },
        {
          text: 'Fases da Missão',
          items: [
            { text: 'Fase 1: Telemetria & Lançamento', link: '/fases/fase-1-telemetria' },
            { text: 'Fase 2: MGPEB - Pouso Marciano', link: '/fases/fase-2-pouso' },
            { text: 'Fase 3: SIC - Matriz Energética', link: '/fases/fase-3-energia' },
            { text: 'Fase 4: SIGIC - Infraestrutura & Grafos', link: '/fases/fase-4-infraestrutura' },
            { text: 'Fase 5: NCAS - Núcleo Cognitivo', link: '/fases/fase-5-cognitivo' },
            { text: 'Fase 6: SCIC - Hardware & ML', link: '/fases/fase-6-scic' },
          ],
        },
        { text: 'Práticas de Engenharia', link: '/engineering-practices' },
        { text: 'Deploy & CI/CD', link: '/deployment' },
      ],
      sidebar: [
        {
          text: '🛰️ Missão & Operações',
          items: [
            { text: 'Mission Briefing', link: '/' },
            { text: 'Launch Checklist & Setup', link: '/getting-started' },
            { text: 'Blueprint Arquitetural', link: '/architecture' },
          ],
        },
        {
          text: '🔴 Fases da Missão (1 a 6)',
          items: [
            { text: 'Fase 1: Telemetria & Lançamento', link: '/fases/fase-1-telemetria' },
            { text: 'Fase 2: MGPEB - Pouso Marciano', link: '/fases/fase-2-pouso' },
            { text: 'Fase 3: SIC - Matriz Energética', link: '/fases/fase-3-energia' },
            { text: 'Fase 4: SIGIC - Infraestrutura & Redes', link: '/fases/fase-4-infraestrutura' },
            { text: 'Fase 5: NCAS - Núcleo Cognitivo', link: '/fases/fase-5-cognitivo' },
            { text: 'Fase 6: SCIC - Hardware, ML & Estruturas', link: '/fases/fase-6-scic' },
          ],
        },
        {
          text: '⚙️ Governança & Qualidade',
          items: [
            { text: 'Engenharia & Qualidade (QA)', link: '/engineering-practices' },
            { text: 'Deploy Contínuo no GitHub Pages', link: '/deployment' },
          ],
        },
      ],
      socialLinks: [{ icon: 'github', link: 'https://github.com/JFrois/PBL-Aurora' }],
      search: {
        provider: 'local',
        options: {
          locales: {
            root: {
              translations: {
                button: {
                  buttonText: 'Buscar telemetria...',
                  buttonAriaLabel: 'Buscar na documentação',
                },
                modal: {
                  noResultsText: 'Nenhum registro encontrado',
                  resetButtonTitle: 'Limpar busca',
                  footer: {
                    selectText: 'selecionar',
                    navigateText: 'navegar',
                    closeText: 'fechar',
                  },
                },
              },
            },
          },
        },
      },
      footer: {
        message: 'Missão Aurora Siger · Base Marciana de Pesquisa · FIAP CC 2026',
        copyright: 'Engenharia de Software Aeroespacial e Sistemas Críticos',
      },
    },
  })
)

// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer').themes.github;
const darkCodeTheme = require('prism-react-renderer').themes.dracula;

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A comprehensive course on embodied intelligence and humanoid systems',
  favicon: 'img/favicon.ico',

  // ✅ Vercel deployment config
  url: 'https://ai-book.vercel.app', // can be any placeholder domain for now
  baseUrl: '/', // 🔴 IMPORTANT: must be "/"

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/Umairshaikh12/AI-book',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig: ({
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
        href: '/', // ✅ FIXED
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Course Book',
        },
        {
          href: 'https://github.com/Umairshaikh12/AI-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Modules',
          items: [
            { label: 'Introduction to Physical AI', to: '/docs/intro/' },
            { label: 'ROS 2 (Robotic Nervous System)', to: '/docs/module-1-ros2/' },
            { label: 'Digital Twin (Gazebo and Unity)', to: '/docs/module-2-digital-twin/' },
            { label: 'AI-Robot Brain (NVIDIA Isaac)', to: '/docs/module-3-ai-brain/' },
            { label: 'Vision-Language-Action (VLA)', to: '/docs/module-4-vla/' },
            { label: 'Capstone Project', to: '/docs/capstone/' },
          ],
        },
        {
          title: 'Community',
          items: [
            { label: 'Stack Overflow', href: 'https://stackoverflow.com/questions/tagged/ros2' },
            { label: 'Discord', href: 'https://discordapp.com/invite/docusaurus' },
          ],
        },
        {
          title: 'More',
          items: [
            { label: 'GitHub', href: 'https://github.com/Umairshaikh12/AI-book' },
          ],
        },
      ],
      copyright:
        `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Course.`,
    },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  }),
};

module.exports = config;

import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkGfm from 'remark-gfm';
import remarkMdxCodeMeta from 'remark-mdx-code-meta';
import searchLocal from '@easyops-cn/docusaurus-search-local';

const config: Config = {
  title: 'test-coverage-mcp',
  tagline: '🔬 A provider-extensible MCP server for test coverage intelligence, with a stable capability-driven tool contract and provider-specific enrichments.',
  favicon: 'img/python_logo_icon.png',

  // Set the production url of your site here
  url: 'https://chisanan232.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/test-coverage-mcp/',
  projectName: 'chisanan232.github.io',
  organizationName: 'Chisanan232',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onDuplicateRoutes: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  markdown: {
    mermaid: true,
    format: 'detect',
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
    mdx1Compat: {
      comments: true,
      admonitions: true,
      headingIds: true,
    },
  },

  presets: [
    [
      'classic',
      {
        docs: false,
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'docs',
        path: 'contents/document',
        routeBasePath: 'docs',
        sidebarPath: './contents/document/sidebars.ts',
        sidebarCollapsible: true,
        showLastUpdateTime: true,
        showLastUpdateAuthor: true,
        editUrl:
          'https://github.com/Chisanan232/test-coverage-mcp/tree/master/docs/',
        versions: {
          current: {
            label: 'Next',
            path: 'next',
            banner: 'unreleased',
            badge: true,
          },
        },
        includeCurrentVersion: true,
        lastVersion: '0.1.0',
      },
    ],
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'dev',
        path: 'contents/development',
        routeBasePath: 'dev',
        sidebarPath: './contents/development/sidebars.ts',
        sidebarCollapsible: true,
        showLastUpdateTime: true,
        showLastUpdateAuthor: true,
        editUrl:
          'https://github.com/Chisanan232/test-coverage-mcp/tree/master/docs/',
        versions: {
          current: {
            label: 'Next',
            path: 'next',
            banner: 'unreleased',
            badge: true,
          },
        },
        includeCurrentVersion: true,
        lastVersion: '0.1.0',
      },
    ],
    [
      '@docusaurus/plugin-content-blog',
      {
        id: 'blog',
        path: 'contents/blog',
        routeBasePath: 'blog',
        showReadingTime: true,
        editUrl:
          'https://github.com/Chisanan232/test-coverage-mcp/tree/master/docs/',
      },
    ],
    [
      searchLocal,
      {
        // Options for docusaurus-search-local
        hashed: true,
        language: ['en'],
        docsRouteBasePath: ['/test-coverage-mcp'],
        docsDir: ['./contents/document', './contents/development'],
        blogDir: ['./contents/blog'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        docsPluginIdForPreferredVersion: 'docs',
        indexDocs: true,
        indexBlog: true,
        indexPages: true,
        searchResultLimits: 8,
        searchResultContextMaxLength: 50,
        removeDefaultStopWordFilter: false,
        removeDefaultStemmer: false,
      },
    ],
  ],

  themes: [
    '@docusaurus/theme-mermaid',
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/python_logo_icon.png',
    navbar: {
      title: 'test-coverage-mcp',
      logo: {
        alt: 'test-coverage-mcp Logo',
        src: 'img/python_logo_icon.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Docs',
          docsPluginId: 'docs',
        },
        {
          type: 'docSidebar',
          sidebarId: 'dev',
          position: 'left',
          label: 'Dev',
          docsPluginId: 'dev',
        },
        {
          to: '/blog',
          label: 'Blog',
          position: 'left',
        },
        {
          type: 'custom-unifiedVersions',
          position: 'right',
          pluginIds: ['docs', 'dev'],
          pluginTitles: {
            docs: 'User Guide',
            dev: 'Developer Guide',
          },
          showBadges: true,
          showDividers: true,
          showNextLabel: true,
          showUnmaintainedLabel: true,
          dropdownItemsBefore: [],
          dropdownItemsAfter: [],
        },
        {
          href: 'https://github.com/Chisanan232/test-coverage-mcp',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Docs',
              to: '/docs/next/introduction',
            },
            {
              label: 'Dev',
              to: '/dev/next',
            },
            {
              label: 'Blog',
              to: '/blog',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/Chisanan232/test-coverage-mcp/issues',
            },
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/Chisanan232/test-coverage-mcp/discussions',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'GitHub Repository',
              href: 'https://github.com/Chisanan232/test-coverage-mcp',
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} - PRESENT, test-coverage-mcp is owned by <a href="https://github.com/Chisanan232">@Chisanan232</a>.<br />Built with <a href="https://docusaurus.io/">Docusaurus</a>.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },

  // Add redirect for homepage
  staticDirectories: ['static'],
  // Homepage redirects to documentation
  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'canonical',
        href: 'https://chisanan232.github.io/test-coverage-mcp/docs/introduction',
      },
    },
  ],
};

export default config;

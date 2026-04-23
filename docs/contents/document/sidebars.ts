import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * Sidebar for the Docs section
 */
const sidebars: SidebarsConfig = {
  docs: [
    {
      type: 'doc',
      id: 'introduction',
      label: '📖 Introduction',
    },
    {
      type: 'category',
      label: '🤟 Getting Started',
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'quick-start/quick-start',
          label: '⚡ Quick Start',
        },
        {
          type: 'doc',
          id: 'quick-start/requirements',
          label: '📋 Requirements',
        },
        {
          type: 'doc',
          id: 'quick-start/installation',
          label: '💾 Installation',
        },
        {
          type: 'doc',
          id: 'quick-start/how-to-run',
          label: '▶️ How to Run',
        },
      ],
    },
    {
      type: 'category',
      label: '🛠️ Guides',
      items: [
        {
          type: 'doc',
          id: 'guides/configuration',
          label: '⚙️ Configuration Guide',
        },
        {
          type: 'doc',
          id: 'guides/provider-development',
          label: '🔌 Provider Development',
        },
      ],
    },
    {
      type: 'category',
      label: '🧰 MCP Tools',
      items: [
        {
          type: 'doc',
          id: 'mcp-tools/overview',
          label: '📚 Tools Overview',
        },
        {
          type: 'doc',
          id: 'mcp-tools/provider-discovery',
          label: '🔍 Provider Discovery',
        },
        {
          type: 'doc',
          id: 'mcp-tools/coverage-analysis',
          label: '📊 Coverage Analysis',
        },
        {
          type: 'doc',
          id: 'mcp-tools/tools-categorization',
          label: '📋 Tools Categorization',
        },
      ],
    },
    {
      type: 'category',
      label: '🏗️ Architecture',
      items: [
        {
          type: 'doc',
          id: 'architecture/overview',
          label: '📐 System Architecture',
        },
      ],
    },
    {
      type: 'category',
      label: '🚀 Deployment',
      items: [
        {
          type: 'doc',
          id: 'deployment/overview',
          label: '📦 Deployment Overview',
        },
      ],
    },
    {
      type: 'category',
      label: '🧑‍💻 API References',
      items: [
        {
          type: 'doc',
          id: 'api-references/api-references',
          label: '📚 API References',
        },
      ],
    },
    {
      type: 'category',
      label: '👋 Contributing',
      items: [
        {
          type: 'doc',
          id: 'contribute/contribute',
          label: '🤝 Contribute',
        },
        {
          type: 'doc',
          id: 'contribute/report-bug',
          label: '🐛 Report Bug',
        },
        {
          type: 'doc',
          id: 'contribute/request-changes',
          label: '💡 Request Changes',
        },
        {
          type: 'doc',
          id: 'contribute/discuss',
          label: '💬 Discuss',
        },
      ],
    },
    {
      type: 'doc',
      id: 'changelog',
      label: '📝 Changelog',
    },
  ],
};

export default sidebars;

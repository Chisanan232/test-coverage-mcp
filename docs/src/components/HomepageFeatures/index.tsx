import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  image: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Provider-Extensible',
    image: require('@site/static/img/easy_to_use.png').default,
    description: (
      <>
        Support multiple coverage providers through a plugin system. Easily extend with custom providers for your specific needs.
      </>
    ),
  },
  {
    title: 'Intelligent Analysis',
    image: require('@site/static/img/python_base.png').default,
    description: (
      <>
        Get comprehensive coverage analysis, trend tracking, and intelligent recommendations.
        Leverage MCP tools for detailed coverage intelligence and insights.
      </>
    ),
  },
];

function Feature({title, image, description}: FeatureItem) {
  return (
    <div className={clsx('col col--6')}>
      <div className="text--center">
        <img className={styles.featureSvg} src={image} alt={title} />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

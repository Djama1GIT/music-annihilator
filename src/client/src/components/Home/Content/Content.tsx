import React from 'react';
import styles from './Content.module.scss';

import { Layout } from "antd";

import Title from "./Title/Title";
import Upload from "./Upload/Upload";
import Features from "./Features/Features";

const { Content } = Layout;

const ContentComponent: React.FC = () => {
  return (
    <Content className={styles.content}>
      <Title />
      <Upload />
      <Features />
    </Content>
  );
};

export default React.memo(ContentComponent);
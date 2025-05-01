import React from 'react';
import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import styles from './PageNotFound.module.scss';

const PageNotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className={styles.page}>
      <Result
        status="404"
        title="404"
        subTitle="Извините, страница, которую вы посетили, не существует."
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            На главную
          </Button>
        }
      />
    </div>
  );
};

export default PageNotFound;
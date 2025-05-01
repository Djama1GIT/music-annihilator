import { QuestionCircleOutlined } from "@ant-design/icons";
import { Button, Modal, Typography } from "antd";
import React from "react";
import { useAnnihilatorStore } from "../../../../store";

const { Title, Paragraph } = Typography;

const HowItWorksModal: React.FC = () => {
  const aboutModalVisible = useAnnihilatorStore(state => state.aboutModalVisible);
  const setAboutModalVisible = useAnnihilatorStore(state => state.setAboutModalVisible);

  const handleCancel = (): void => {
    setAboutModalVisible(false);
  };

  const modalTitle: React.ReactNode = (
    <div>
      <QuestionCircleOutlined/>
      <span> Как это работает</span>
    </div>
  );

  const modalFooter: React.ReactNode[] = [
    <Button key="close" onClick={handleCancel}>
      Закрыть
    </Button>
  ];

  return (
    <Modal
      title={modalTitle}
      open={aboutModalVisible}
      onCancel={handleCancel}
      footer={modalFooter}
      width={800}
    >
      <Title level={4}>Технология Spleeter</Title>
      <Paragraph>
        Наш сервис использует технологию Spleeter, разработанную для разделения аудио
        с помощью искусственного интеллекта.
      </Paragraph>

      <Title level={5}>Основные возможности:</Title>
      <ul>
        <li>Поддержка 2, 4 и 5 стемов (отдельных дорожек)</li>
        <li>Высокое качество разделения благодаря нейросетевой модели</li>
        <li>Быстрая обработка даже длинных дорожек</li>
      </ul>

      <Title level={5}>Как это работает технически:</Title>
      <Paragraph>
        Spleeter использует предобученную модель U-Net, которая была обучена на большом наборе данных
        для распознавания и разделения различных компонентов аудио.
        Алгоритм анализирует спектрограмму аудиофайла и выделяет отдельные составляющие.
      </Paragraph>
    </Modal>
  );
};

export default React.memo(HowItWorksModal);
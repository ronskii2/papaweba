import MainLayout from '@/components/common/MainLayout'

export default function Home() {
  return (
    <MainLayout>
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Добро пожаловать в Ложку</h1>
        <p className="text-xl text-gray-600 mb-8">
          Ваш умный ассистент для решения повседневных задач
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Общение</h3>
            <p className="text-gray-600">
              Интеллектуальный собеседник для любых тем
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Творчество</h3>
            <p className="text-gray-600">
              Создание изображений и обработка контента
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-lg font-semibold mb-2">Анализ</h3>
            <p className="text-gray-600">
              Работа с документами и данными
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}

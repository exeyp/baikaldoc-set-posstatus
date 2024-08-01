class DataProcessor:
    # {'isnRefRubric': 128598650, 'eosSstuStatus': 'Находится на рассмотрении', 'posStatusRub': None}
    # {'isnRefRubric': 128661624, 'eosSstuStatus': 'Находится на рассмотрении', 'posStatusRub': 'Передано в вышестоящую организацию'}
    # {'Находится на рассмотрении': 'Назначен исполнитель', 'Рассмотрение продлено': 'Перенос срока обработки утвержден. Отправлен ответ Заявителю', 'Оставлено без ответа автору': 'Отклонено модератором', 'Рассмотрено. Разъяснено': 'Отправлен ответ заявителю', 'Рассмотрено. Не поддержано': 'Отправлен ответ заявителю', 'Дан ответ автору': 'Отправлен ответ заявителю', 'Рассмотрено. Поддержано': 'Отправлен ответ заявителю', 'Направлено по компетенции': 'Направлено в подведомственную организацию'}
    @staticmethod
    def process_and_build_mutation_queries(data, status_map):
        processed_data = []
        # mutation_variables_list = []
        BATCH_SIZE = 20
        mutation_template = "mutation UpdateArRubricValues {{ {mutations} }}"
        mutation_queries = []

        for item in data:
            if item['posStatusRub'] is None:
                item['posStatusRub'] = status_map.get(item.get('eosSstuStatus'))
            processed_data.append(item)
            
            # mutation_variables = {
            #         "input": {
            #             "data": {
            #                 "isnRefRubric": item['isnRefRubric'],
            #                 "posStatusRub": item['posStatusRub']
            #             }
            #         }
            #     }
            # mutation_variables_list.append(mutation_variables)

        for i in range(0, len(processed_data), BATCH_SIZE):
            batch = processed_data[i:i + BATCH_SIZE]
            mutations = []

            for idx, item in enumerate(batch):
                mutation = (
                    f"update{idx}: updateArRubricValue(input: {{"
                    f"clientMutationId: \"{mutation_name}\","
                    f"data: {{"
                    f"isnRefRubric: {item['isnRefRubric']},"
                    f"posStatusRub: \"{item['posStatusRub']}\""
                    f"}}"
                    f"}}) {{"
                    f"success,"
                    f"message,"
                    f"messageCode,"
                    f"messageData,"
                    f"systemMessage,"
                    f"data {{"
                    f"isnRefRubric,"
                    f"posStatusRub"
                    f"}}"
                    f"}}"
                )
                mutations.append(mutation.strip())

            mutation_query = mutation_template.format(mutations=" ".join(mutations))
            mutation_queries.append(mutation_query)

        return mutation_queries

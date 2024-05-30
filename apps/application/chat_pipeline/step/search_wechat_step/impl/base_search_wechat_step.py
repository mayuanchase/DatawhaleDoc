# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_search_dataset_step.py
    @date：2024/1/10 10:33
    @desc:
"""
import os
from typing import List, Dict
from django.db.models import QuerySet
from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.step.search_dataset_step.i_search_dataset_step import ISearchDatasetStep
from application.chat_pipeline.step.search_wechat_step.i_search_wechat_step import ISearchWechatStep
from application.chat_pipeline.step.search_wechat_step.impl import search_wechat
from application.chat_pipeline.step.search_wechat_step.impl.search_wechat import MetaContent
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.db.search import native_search
from common.util.file_util import get_file_content
from dataset.models import Paragraph
from embedding.models import SearchMode
from smartdoc.conf import PROJECT_DIR
import logging


class BaseSearchWechatStep(ISearchWechatStep):

    @staticmethod
    def convert_meta_list_to_paragraph_list(meta_list: List[MetaContent], status: str, is_active: bool,
                                            comprehensive_score: float, similarity: float, dataset_name: str,
                                            document_name: str, hit_handling_method: str,
                                            directly_return_similarity: float) -> List[ParagraphPipelineModel]:
        paragraph_list = []
        for i, meta in enumerate(meta_list):
            paragraph = ParagraphPipelineModel(
                _id=str(i),
                document_id=f"doc_{i}",
                dataset_id=f"ds_{i}",
                content=meta.content,
                title=meta.nickname,  # Assuming title is the nickname
                status=status,
                is_active=is_active,
                comprehensive_score=comprehensive_score,
                similarity=similarity,
                dataset_name=dataset_name,
                document_name=document_name,
                hit_handling_method=hit_handling_method,
                directly_return_similarity=directly_return_similarity
            )
            paragraph_list.append(paragraph)
        return paragraph_list

    def execute(self, problem_text: str, dataset_id_list: List[str], exclude_document_id_list: List[str],
                exclude_paragraph_id_list: List[str], top_n: int, similarity: float, padding_problem_text: str = None,
                search_mode: str = None, wechat_name=None, **kwargs) -> List[ParagraphPipelineModel]:
        info = search_wechat.get_wechat_info(wechat_name)

        paragraph_list = self.convert_meta_list_to_paragraph_list(
            meta_list=info,
            status="active",
            is_active=True,
            comprehensive_score=9.5,
            similarity=0.85,
            dataset_name="Dataset Name",
            document_name="Document Name",
            hit_handling_method="Method",
            directly_return_similarity=0.9
        )

        return paragraph_list

    def list_paragraph(self, embedding_list, vector):
        # Implement your method to list paragraphs based on embedding_list and vector
        pass

    def reset_paragraph(self, paragraph, embedding_list):
        # Implement your method to reset a paragraph based on the embedding list
        pass

    @staticmethod
    def reset_paragraph(paragraph: Dict, embedding_list: List) -> ParagraphPipelineModel:
        filter_embedding_list = [embedding for embedding in embedding_list if
                                 str(embedding.get('paragraph_id')) == str(paragraph.get('id'))]
        if filter_embedding_list:
            find_embedding = filter_embedding_list[-1]
            return (ParagraphPipelineModel.builder()
                    .add_paragraph(paragraph)
                    .add_similarity(find_embedding.get('similarity'))
                    .add_comprehensive_score(find_embedding.get('comprehensive_score'))
                    .add_dataset_name(paragraph.get('dataset_name'))
                    .add_document_name(paragraph.get('document_name'))
                    .add_hit_handling_method(paragraph.get('hit_handling_method'))
                    .add_directly_return_similarity(paragraph.get('directly_return_similarity'))
                    .build())

    @staticmethod
    def get_similarity(paragraph, embedding_list: List):
        filter_embedding_list = [embedding for embedding in embedding_list if
                                 str(embedding.get('paragraph_id')) == str(paragraph.get('id'))]
        if filter_embedding_list:
            find_embedding = filter_embedding_list[-1]
            return find_embedding.get('comprehensive_score')
        return 0

    @staticmethod
    def list_paragraph(embedding_list: List, vector):
        paragraph_id_list = [row.get('paragraph_id') for row in embedding_list]
        if not paragraph_id_list:
            return []
        paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                       get_file_content(
                                           os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                        'list_dataset_paragraph_by_paragraph_id.sql')),
                                       with_table_name=True)
        # 如果向量库中存在脏数据 直接删除
        if len(paragraph_list) != len(paragraph_id_list):
            exist_paragraph_list = [row.get('id') for row in paragraph_list]
            for paragraph_id in paragraph_id_list:
                if paragraph_id not in exist_paragraph_list:
                    vector.delete_by_paragraph_id(paragraph_id)
        # 如果存在直接返回的则取直接返回段落
        hit_handling_method_paragraph = [paragraph for paragraph in paragraph_list if
                                         (paragraph.get(
                                             'hit_handling_method') == 'directly_return' and BaseSearchWechatStep.get_similarity(
                                             paragraph, embedding_list) >= paragraph.get(
                                             'directly_return_similarity'))]
        if hit_handling_method_paragraph:
            # 找到评分最高的
            return [sorted(hit_handling_method_paragraph,
                           key=lambda p: BaseSearchWechatStep.get_similarity(p, embedding_list))[-1]]
        return paragraph_list

    def get_details(self, manage, **kwargs):
        step_args = self.context['step_args']

        return {
            'step_type': 'search_step',
            'paragraph_list': [row.to_dict() for row in self.context['paragraph_list']],
            'run_time': self.context['run_time'],
            'problem_text': step_args.get(
                'padding_problem_text') if 'padding_problem_text' in step_args else step_args.get('problem_text'),
            'model_name': EmbeddingModel.get_embedding_model().model_name,
            'message_tokens': 0,
            'answer_tokens': 0,
            'cost': 0
        }

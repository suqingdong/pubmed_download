#!/usr/bin/env python
#-*- encoding: utf8 -*-
import re
import sys

import lxml.etree as ET

reload(sys)
sys.setdefaultencoding('utf-8')


def parse_pubmed_xml(text, translator=None):

    tree = ET.fromstring(text)

    if tree.find('PubmedArticle') is None:
        yield None
    else:
        for PubmedArticle in tree.iterfind('PubmedArticle'):
            MedlineCitation = PubmedArticle.find('MedlineCitation')

            pmid = int(MedlineCitation.find('PMID').text)

            Article = MedlineCitation.find('Article')


            e_issn = ''.join(Article.xpath('Journal/ISSN[@IssnType="Electronic"]/text()')) or '.'
            issn = ''.join(Article.xpath('Journal/ISSN[@IssnType="Print"]/text()')) or '.'
            if issn == '.':
                issn = ''.join(MedlineCitation.xpath('MedlineJournalInfo/ISSNLinking/text()')) or '.'

            journal = ''.join(Article.xpath('Journal/Title/text()')) or '.'
            journal_abbr = ''.join(Article.xpath('Journal/ISOAbbreviation/text()')) or '.'
            if journal_abbr != '.':
                journal_abbr = journal_abbr.replace('.', '')

            pubdate = ' '.join(Article.xpath('Journal/JournalIssue/PubDate/*/text()'))

            title = Article.find('ArticleTitle').text

            # ==============================================
            # 1 没有Abstract
            # 2 只有1个AbstractText
            # 3 有多个AbstractText，获取Label
            #
            # * 待解决：编码问题
            # ==============================================
            AbstractTexts = Article.xpath('Abstract/AbstractText')
            if not AbstractTexts:
                abstract = '.'
            elif len(AbstractTexts) == 1:
                abstract = ''.join(AbstractTexts[0].itertext()) or '.'
            else:
                abstract = []
                for each in AbstractTexts:
                    # print dir(each)
                    label = each.attrib.get('Label')
                    text = ''.join(each.itertext())
                    if label:
                        abstract.append('{}: {}'.format(label, text))
                    else:
                        abstract.append(text)
                abstract = '\n'.join(abstract)

            # 特殊字符处理
            special_chars = u'\u202f|\u2009'.encode('utf-8')
            abstract = re.sub(special_chars, '', abstract)

            # abstract = abstract.encode('utf-8')

            author_list = []
            for author in Article.xpath('AuthorList/Author'):
                lastname = author.xpath('LastName/text()')
                initials = author.xpath('Initials/text()')
                suffix = author.xpath('Suffix/text()')
                author_list.append(' '.join(lastname + initials + suffix))

            publication_types = Article.xpath('PublicationTypeList/PublicationType/text()')

            pmc = doi = '.'
            ArticleIds = PubmedArticle.xpath('PubmedData/ArticleIdList/ArticleId')
            if ArticleIds:
                for each in ArticleIds:
                    if each.attrib['IdType'] == 'pmc':
                        pmc = each.text
                    elif each.attrib['IdType'] == 'doi':
                        doi = each.text

            fields = '''
                pmid issn journal journal_abbr pubdate title abstract
                author_list publication_types pmc doi e_issn'''.split()

            if translator:
                abstract_cn = '.'
                if abstract != '.':
                    abstract_cn = translator.translate(abstract, dest='zh-cn').text
                fields.append('abstract_cn')

            tmpdict = locals()
            context = {field: tmpdict[field] for field in fields}

            yield context


if __name__ == '__main__':

    import requests

    pmid = '1,20002000,30737105'
    pmid = '30004117'
    pmid = '30004023'
    pmid = '30004170'

    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml'.format(pmid)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101'}
    resp = requests.get(url, headers=headers)
    result = parse_pubmed_xml(resp.text)
    abstract = list(result)[-1]['abstract']
    # print repr(abstract)
    print abstract
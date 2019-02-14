
INSERT INTO "address" (address_id, house_name_number, street, town_city, county, country, postcode)
VALUES	(1, '1', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(2, '10', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(3, '11', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(4, '20', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(5, '21', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),

		(6, '30', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(7, '31', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN'),
		(8, '32', 'Digital Street', 'Bristol', 'Bristol', 'England', 'BS2 8EN');
ALTER SEQUENCE "address_address_id_seq" RESTART WITH 9;

INSERT INTO "user" (identity, first_name, last_name, email_address, phone_number, address_id)
VALUES	('1', 'Lisa', 'White', 'lisa.white@example.com', '+447700900354', 2),
		('2', 'David', 'Jones', 'david.jones@example.com', '+447700900827', 3),

		('3', 'Natasha', 'Powell', 'natasha.powell@example.com', '+447700900027', 4),
		('4', 'Samuel', 'Barnes', 'samuel.barnes@example.com', '+447700900534', 5),

		('5', 'Jim', 'Smith', 'jim.smith@example.com', '+447700900815', 6),
		('6', 'Martin', 'Keats', 'martin.keats@example.com', '+447700900133', 7),
		('7', 'Holly', 'Windsor', 'holly.windsor@example.com', '+447700900970', 8);

INSERT INTO "case" (case_type, status, case_reference, created_at, title_number, assigned_staff_id, client_id, counterparty_id, counterparty_conveyancer_org, counterparty_conveyancer_contact_id, address_id)
VALUES	('sell', 'active', 'ABCD123', '2018-11-01 09:00:00.000000', 'ZQV888860', 3, 1, 2, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 1),
		('sell', 'active', 'KSYB294', '2018-11-01 09:00:00.000000', 'ZQV888861', 3, 5, 2, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 6),
		('sell', 'active', 'MAYN467', '2018-11-01 09:00:00.000000', 'ZQV888862', 3, 6, 2, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 7),
		('buy', 'active', 'MNAW046', '2018-11-01 09:00:00.000000', 'ZQV888863', 3, 2, 7, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 8),
		('sell', 'active', 'NAYR825', '2018-11-01 09:00:00.000000', 'RTV237231', 3, 1, 7, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 2),
		('sell', 'active', 'NCAY914', '2018-11-01 09:00:00.000000', 'RTV237232', 3, 2, 6, 'O=Conveyancer2,L=Plymouth,C=GB', 4, 3),
		('sell', 'active', 'XXSA013', '2018-11-01 09:00:00.000000', 'RTV237233', 1, 3, 5, 'O=Conveyancer2,L=Plymouth,C=GB', 2, 4),
		('buy', 'active', 'PAHD134', '2018-11-01 09:00:00.000000', 'RTV237234', 6, 2, 4, 'O=Conveyancer2,L=Plymouth,C=GB', 1, 5);

INSERT INTO "restriction" (restriction_id, restriction_type, restriction_text)
VALUES	('BX102', 'CBCR', 'RESTRICTION: No disposition of the registered estate by the proprietor of the registered estate is to be registered without a written consent signed by the proprietor for the time being of the Charge dated *CD* in favour of *CP* referred to in the Charges Register.'),
		('BX750', 'ORES', 'RESTRICTION: No disposition by the proprietor of the registered estate to which section 36 or section 38 of the Charities Act 1993 applies is to be registered unless the instrument contains a certificate complying with section 37(2) or section 39(2) of that Act as appropriate.');
